import math
import random
import time
import copy


class MCTSNode:
    def __init__(self, state, parent=None, move=None, player=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.player = player

        self.children = []
        self.untried_moves = []

        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration_constant=1.41):
        best_score = float("-inf")
        best_child = None

        for child in self.children:
            if child.visits == 0:
                return child

            exploitation = child.value / child.visits
            exploration = exploration_constant * math.sqrt(
                math.log(self.visits + 1) / child.visits
            )

            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_child = child

        return best_child


class MCTSAgent:
    """
    MCTS básico compatible con la plataforma Morris.

    Esta versión usa:
    - selección con UCB1
    - expansión con movimientos legales
    - simulación aleatoria
    - retropropagación
    """

    def __init__(self, agent_number, time_limit=0.15, exploration_constant=1.41):
        self.agent_number = agent_number
        self.opponent_number = 2 if agent_number == 1 else 1
        self.time_limit = time_limit
        self.exploration_constant = exploration_constant

    def make_move(self, state):
        legal_moves = [
            move for move in list(state.legal_moves(self.agent_number))
            if move[0] != "capture"
        ]

        if len(legal_moves) == 0:
            return None

        if len(legal_moves) == 1:
            return legal_moves[0]

        root = MCTSNode(
            state=self._clone_state(state),
            parent=None,
            move=None,
            player=self.agent_number
        )

        root.untried_moves = legal_moves[:]

        start_time = time.time()

        while time.time() - start_time < self.time_limit:
            node = root

            # 1. Selection
            while node.is_fully_expanded() and len(node.children) > 0:
                node = node.best_child(self.exploration_constant)

            # 2. Expansion
            if len(node.untried_moves) > 0:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)

                try:
                    next_state = self._apply_move(node.state, move, node.player)
                except Exception:
                    continue

                next_player = self._next_player(node.player)

                child = MCTSNode(
                    state=next_state,
                    parent=node,
                    move=move,
                    player=next_player
                )

                try:
                    child.untried_moves = list(next_state.legal_moves(next_player))
                except Exception:
                    child.untried_moves = []

                node.children.append(child)
                node = child

            # 3. Simulation
            result = self._simulate(node.state, node.player)

            # 4. Backpropagation
            self._backpropagate(node, result)

        if len(root.children) == 0:
            return random.choice(legal_moves)

        best_child = max(root.children, key=lambda child: child.visits)

        if best_child.move in legal_moves:
            return best_child.move

        return random.choice(legal_moves)

    def _clone_state(self, state):
        """
        Clona el estado usando el método copy() propio de GameState.
        """
        if hasattr(state, "copy"):
            return state.copy()

        return copy.deepcopy(state)

    def _apply_move(self, state, move, player=None):
        """
        Aplica un movimiento de forma compatible con game_engine.py.

        En esta plataforma:
        - state.apply_move(move) aplica place/move.
        - state.apply_capture(pos) aplica capturas.
        - Los movimientos tienen formato: (kind, src, dst)
        """

        new_state = self._clone_state(state)

        kind, src, dst = move

        if kind == "capture":
            new_state.apply_capture(dst)
            return new_state

        new_state.apply_move(move)
        return new_state

    def _simulate(self, state, player, max_depth=80):
        simulation_state = self._clone_state(state)
        current_player = player

        for _ in range(max_depth):
            winner = self._get_winner(simulation_state)

            if winner is not None:
                return self._score_result(winner)

            try:
                legal_moves = list(simulation_state.legal_moves(current_player))
            except Exception:
                return 0.0

            if len(legal_moves) == 0:
                winner = self._next_player(current_player)
                return self._score_result(winner)

            move = random.choice(legal_moves)

            try:
                simulation_state = self._apply_move(
                    simulation_state,
                    move,
                    current_player
                )
            except Exception:
                return 0.0

            current_player = self._next_player(current_player)

        return 0.0

    def _get_winner(self, state):
        """
        Detecta ganador si la plataforma lo permite.
        Si no existe método claro, devuelve None.
        """

        if hasattr(state, "winner"):
            winner = state.winner
            if callable(winner):
                return winner()
            return winner

        if hasattr(state, "get_winner"):
            return state.get_winner()

        if hasattr(state, "is_terminal"):
            try:
                if state.is_terminal():
                    if hasattr(state, "result"):
                        return state.result()
            except Exception:
                return None

        return None

    def _score_result(self, winner):
        if winner == self.agent_number:
            return 1.0

        if winner == self.opponent_number:
            return -1.0

        return 0.0

    def _backpropagate(self, node, result):
        current = node
        value = result

        while current is not None:
            current.visits += 1
            current.value += value

            value = -value
            current = current.parent

    def _next_player(self, player):
        return 2 if player == 1 else 1