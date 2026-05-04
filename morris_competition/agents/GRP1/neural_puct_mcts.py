# neural_puct_mcts.py
#
# MCTS estilo AlphaZero usando PUCT + red neuronal policy/value.
#
# Este archivo es experimental y NO reemplaza al agente estable todavía.
#
# Objetivo:
# - Usar MorrisNet para obtener:
#     P(s,a): prior de política
#     V(s): valor del estado
# - Usar PUCT para seleccionar acciones.
# - Devolver:
#     best_move
#     visit_policy: distribución de visitas para entrenamiento AlphaZero.

import math
import random
from collections import defaultdict

import torch

from .model import MorrisNet
from .neural_utils import (
    encode_state,
    action_to_index,
    ACTION_SIZE,
)


class NeuralPUCTNode:
    """
    Nodo usado por NeuralPUCTMCTS.

    Cada nodo guarda:
    - state: estado del juego.
    - player: jugador que debe mover en este estado.
    - parent: nodo padre.
    - move: movimiento que llevó a este nodo.
    - prior: P(s,a), probabilidad previa dada por la red.
    - children: acciones expandidas.
    - visit_count: N(s)
    - value_sum: suma de valores acumulados.
    """

    def __init__(self, state, player, parent=None, move=None, prior=0.0):
        self.state = state
        self.player = player
        self.parent = parent
        self.move = move
        self.prior = prior

        self.children = {}

        self.visit_count = 0
        self.value_sum = 0.0

        self.is_expanded = False

    @property
    def q_value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


class NeuralPUCTMCTS:
    """
    MCTS con PUCT guiado por red neuronal.

    Esta clase implementa una versión AlphaZero-like:

    Selection:
        usa PUCT = Q + c_puct * P * sqrt(N_parent) / (1 + N_child)

    Expansion/Evaluation:
        usa MorrisNet para obtener policy priors y value.

    Backpropagation:
        propaga el value alternando signo porque el juego es de suma cero.
    """

    def __init__(
        self,
        agent_number,
        model=None,
        checkpoint_path=None,
        simulations=80,
        c_puct=1.5,
        device=None,
        temperature=1.0,
    ):
        self.agent_number = agent_number
        self.opponent_number = 2 if agent_number == 1 else 1

        self.simulations = simulations
        self.c_puct = c_puct
        self.temperature = temperature

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device

        if model is not None:
            self.model = model
        else:
            self.model = MorrisNet()

        if checkpoint_path is not None:
            self._load_checkpoint(checkpoint_path)

        self.model.to(self.device)
        self.model.eval()

    def _load_checkpoint(self, checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            self.model.load_state_dict(checkpoint)

    def search(self, state, return_policy=True):
        """
        Ejecuta PUCT-MCTS desde el estado dado.

        Returns:
            best_move
            visit_policy
        """

        legal_moves = self._legal_non_capture_moves(state, self.agent_number)

        if not legal_moves:
            if return_policy:
                return None, [0.0] * ACTION_SIZE
            return None

        if len(legal_moves) == 1:
            policy = [0.0] * ACTION_SIZE
            policy[action_to_index(legal_moves[0])] = 1.0

            if return_policy:
                return legal_moves[0], policy
            return legal_moves[0]

        root = NeuralPUCTNode(
            state=state.copy(),
            player=self.agent_number,
            parent=None,
            move=None,
            prior=1.0,
        )

        self._expand_and_evaluate(root)

        for _ in range(self.simulations):
            node = root

            # 1. Selection
            while node.is_expanded and node.children:
                node = self._select_child(node)

            # 2. Evaluation / Expansion
            value = self._evaluate_terminal(node)

            if value is None:
                value = self._expand_and_evaluate(node)

            # 3. Backpropagation
            self._backpropagate(node, value)

        visit_policy = self._build_visit_policy(root)

        best_move = self._select_final_move(root)

        if best_move not in legal_moves:
            best_move = random.choice(legal_moves)

        if return_policy:
            return best_move, visit_policy

        return best_move

    def search_capture(self, state, return_policy=True):
        """
        Búsqueda para captura.

        Para mantener seguridad, usa la política de red sobre acciones capture.
        Si no hay checkpoint fuerte, esto puede ser débil; por eso AlphaZeroAgent
        puede seguir usando captura heurística si se desea.
        """

        legal_moves = list(state.legal_moves(self.agent_number))
        capture_moves = [move for move in legal_moves if move[0] == "capture"]

        if not capture_moves:
            if return_policy:
                return None, [0.0] * ACTION_SIZE
            return None

        encoded = encode_state(state, self.agent_number)
        legal_indices = [action_to_index(move) for move in capture_moves]

        policy_probs, _ = self._predict(encoded, legal_indices)

        best_move = max(
            capture_moves,
            key=lambda move: float(policy_probs[action_to_index(move)])
        )

        visit_policy = [0.0] * ACTION_SIZE
        visit_policy[action_to_index(best_move)] = 1.0

        if return_policy:
            return best_move, visit_policy

        return best_move

    def _select_child(self, node):
        best_score = float("-inf")
        best_child = None

        parent_visits = max(1, node.visit_count)

        for child in node.children.values():
            q = child.q_value

            u = (
                self.c_puct
                * child.prior
                * math.sqrt(parent_visits)
                / (1 + child.visit_count)
            )

            score = q + u

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def _expand_and_evaluate(self, node):
        """
        Expande un nodo usando policy priors de la red.
        Devuelve value desde la perspectiva del jugador del nodo.
        """

        legal_moves = list(node.state.legal_moves(node.player))

        if not legal_moves:
            node.is_expanded = True
            return -1.0

        encoded = encode_state(node.state, node.player)
        legal_indices = [action_to_index(move) for move in legal_moves]

        policy_probs, value = self._predict(encoded, legal_indices)

        for move in legal_moves:
            idx = action_to_index(move)
            prior = float(policy_probs[idx])

            next_state = node.state.copy()
            self._apply_action(next_state, move)

            next_player = next_state.cur

            child = NeuralPUCTNode(
                state=next_state,
                player=next_player,
                parent=node,
                move=move,
                prior=prior,
            )

            node.children[move] = child

        node.is_expanded = True

        return value

    def _predict(self, encoded_state, legal_indices):
        """
        Corre la red y aplica máscara de acciones legales.
        """

        with torch.no_grad():
            x = torch.tensor(
                encoded_state,
                dtype=torch.float32,
                device=self.device,
            ).unsqueeze(0)

            policy_logits, value = self.model(x)
            policy_logits = policy_logits.squeeze(0)

            mask = torch.full_like(policy_logits, float("-inf"))
            mask[legal_indices] = policy_logits[legal_indices]

            policy_probs = torch.softmax(mask, dim=0)

            return policy_probs.cpu(), float(value.item())

    def _evaluate_terminal(self, node):
        """
        Si el nodo es terminal, devuelve value.
        Si no es terminal, devuelve None.

        El value se calcula desde la perspectiva del jugador del nodo.
        """

        if not node.state.is_terminal():
            return None

        winner = node.state.winner()

        if winner is None:
            return 0.0

        if winner == node.player:
            return 1.0

        return -1.0

    def _backpropagate(self, node, value):
        """
        Propaga el valor hacia la raíz alternando signo.

        Como el juego es de suma cero, el valor para el padre es el negativo
        del valor para el hijo.
        """

        current = node
        current_value = value

        while current is not None:
            current.visit_count += 1
            current.value_sum += current_value

            current_value = -current_value
            current = current.parent

    def _build_visit_policy(self, root):
        """
        Construye vector de tamaño ACTION_SIZE con distribución de visitas.
        """

        visit_policy = [0.0] * ACTION_SIZE

        total_visits = sum(child.visit_count for child in root.children.values())

        if total_visits == 0:
            legal_moves = self._legal_non_capture_moves(root.state, self.agent_number)
            if legal_moves:
                prob = 1.0 / len(legal_moves)
                for move in legal_moves:
                    visit_policy[action_to_index(move)] = prob
            return visit_policy

        for move, child in root.children.items():
            idx = action_to_index(move)
            visit_policy[idx] = child.visit_count / total_visits

        return visit_policy

    def _select_final_move(self, root):
        """
        Selecciona movimiento final usando visitas.

        Para competencia/evaluación se usa argmax de visitas.
        """

        if not root.children:
            return None

        return max(
            root.children.items(),
            key=lambda item: item[1].visit_count
        )[0]

    def _apply_action(self, state, move):
        """
        Aplica acción en el GameState.

        El motor usa:
        - apply_move(("place", None, dst))
        - apply_move(("move", src, dst))
        - apply_capture(pos)
        """

        kind, src, dst = move

        if kind == "capture":
            state.apply_capture(dst)
        else:
            state.apply_move(move)

    def _legal_non_capture_moves(self, state, player):
        legal_moves = list(state.legal_moves(player))
        return [move for move in legal_moves if move[0] != "capture"]