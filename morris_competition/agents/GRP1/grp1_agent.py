import random

from .mcts_puct import MCTSAgent
from .utils import *


class GRP1:
    """
    Agente del Grupo 1.

    La plataforma de competencia llama:
    - choose_move(state, move_choice_dict)
    - choose_capture(state, capture_choice_dict)

    Por eso este archivo actúa como adaptador entre la plataforma
    y nuestro MCTS.
    """

    def __init__(self, agent_num, name="GRP1"):
        self.name = name
        self.number_of_wins = 0
        self.agent_number = agent_num

        self.mcts_moves = 0
        self.random_fallbacks = 0
        self.illegal_mcts_moves = 0
        self.immediate_mill_moves = 0

        try:
            self.tree = call_load_file()
        except Exception:
            self.tree = None

        self.mcts = MCTSAgent(agent_number=agent_num)

    def choose_move(self, state, move_choice_dict):
        legal_moves = state.legal_moves(self.agent_number)
        legal_moves = [move for move in legal_moves if move[0] != "capture"]

        if len(legal_moves) == 0:
            move_choice_dict["move_choice"] = None
            return None

        immediate_mill_move = self._find_immediate_mill_move(state, legal_moves)

        if immediate_mill_move is not None:
            self.immediate_mill_moves += 1
            move_choice_dict["move_choice"] = immediate_mill_move
            return immediate_mill_move

        try:
            move = self.mcts.make_move(state)
        except Exception as error:
            self.random_fallbacks += 1
            print(f"[GRP1] Error en MCTS, usando random fallback: {error}")
            move = random.choice(legal_moves)

        if move not in legal_moves:
            self.illegal_mcts_moves += 1
            print("[GRP1] MCTS devolvió movimiento ilegal, usando random fallback.")
            move = random.choice(legal_moves)
        else:
            self.mcts_moves += 1

        move_choice_dict["move_choice"] = move
        return move

    def choose_capture(self, state, capture_choice_dict):
        legal_moves = state.legal_moves(self.agent_number)

        if len(legal_moves) == 0:
            capture_choice_dict["capture_choice"] = None
            return None

        capture_moves = [move for move in legal_moves if move[0] == "capture"]

        if len(capture_moves) == 0:
            move = random.choice(legal_moves)
            capture_choice_dict["capture_choice"] = move[2]
            return move[2]

        best_capture = None
        best_score = float("-inf")

        for move in capture_moves:
            pos = move[2]
            score = self._score_capture(state, pos)

            if score > best_score:
                best_score = score
                best_capture = pos

        capture_choice_dict["capture_choice"] = best_capture
        return best_capture

    def _score_capture(self, state, pos):
        """
        Asigna puntaje a una pieza rival candidata a captura.
        Mayor puntaje = mejor captura.
        """

        score = 0

        opponent_player = 2 if self.agent_number == 1 else 1

        # 1. Capturar piezas con alta conectividad suele ser mejor.
        neighbors = self._get_neighbors(pos)
        occupied_neighbors = 0

        for n in neighbors:
            if state.board[n] == opponent_player:
                occupied_neighbors += 1

        score += occupied_neighbors

        # 2. Capturar piezas que participan en amenazas de molino.
        score += 4 * self._count_potential_mills(state, pos, opponent_player)

        # 3. Capturar piezas centrales/conectadas suele reducir movilidad.
        score += len(neighbors) * 0.5

        return score

    def _get_neighbors(self, pos):
        neighbors = {
            0: [1, 9],
            1: [0, 2, 4],
            2: [1, 14],
            3: [4, 10],
            4: [1, 3, 5, 7],
            5: [4, 13],
            6: [7, 11],
            7: [4, 6, 8],
            8: [7, 12],
            9: [0, 10, 21],
            10: [3, 9, 11, 18],
            11: [6, 10, 15],
            12: [8, 13, 17],
            13: [5, 12, 14, 20],
            14: [2, 13, 23],
            15: [11, 16],
            16: [15, 17, 19],
            17: [12, 16],
            18: [10, 19],
            19: [16, 18, 20, 22],
            20: [13, 19],
            21: [9, 22],
            22: [19, 21, 23],
            23: [14, 22],
        }

        return neighbors.get(pos, [])

    def _count_potential_mills(self, state, pos, player):
        mills = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (9, 10, 11), (12, 13, 14), (15, 16, 17),
            (18, 19, 20), (21, 22, 23),
            (0, 9, 21), (3, 10, 18), (6, 11, 15),
            (1, 4, 7), (16, 19, 22),
            (8, 12, 17), (5, 13, 20), (2, 14, 23)
        ]

        count = 0

        for mill in mills:
            if pos not in mill:
                continue

            player_count = 0
            empty_count = 0

            for p in mill:
                if state.board[p] == player:
                    player_count += 1
                elif state.board[p] == 0:
                    empty_count += 1

            # Si el rival tiene 2 piezas y 1 espacio, es amenaza directa.
            if player_count == 2 and empty_count == 1:
                count += 1

        return count
    def _find_immediate_mill_move(self, state, legal_moves):
        """
        Busca un movimiento legal que forme molino inmediatamente.
        Si el estado no soporta copy/apply_move, se ignora esta mejora.
        """

        if not hasattr(state, "copy"):
            return None

        for move in legal_moves:
            try:
                copied_state = state.copy()
                need_capture, src, dst = copied_state.apply_move(move)

                if need_capture:
                    return move

            except Exception:
                continue

        return None
