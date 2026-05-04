# alphazero_agent.py
#
# Agente experimental AlphaZero-like.
#
# IMPORTANTE:
# Este agente NO reemplaza todavía a GRP1 estable.
# Se usa para evaluación separada.

from pathlib import Path
import random

from .neural_puct_mcts import NeuralPUCTMCTS


class AlphaZeroAgent:
    def __init__(
        self,
        agent_num,
        name="AlphaZero-GRP1",
        checkpoint_path=None,
        simulations=40,
    ):
        self.agent_number = agent_num
        self.name = name
        self.number_of_wins = 0

        if checkpoint_path is None:
            root = Path(__file__).resolve().parents[2]
            default_checkpoint = root / "training" / "checkpoints" / "morris_net.pt"

            if default_checkpoint.exists():
                checkpoint_path = default_checkpoint
            else:
                checkpoint_path = None

        self.mcts = NeuralPUCTMCTS(
            agent_number=agent_num,
            checkpoint_path=checkpoint_path,
            simulations=simulations,
        )

    def choose_move(self, state, move_choice_dict):
        legal_moves = [
            move for move in state.legal_moves(self.agent_number)
            if move[0] != "capture"
        ]

        if not legal_moves:
            move_choice_dict["move_choice"] = None
            return None

        try:
            move, _ = self.mcts.search(state, return_policy=True)
        except Exception as error:
            print(f"[AlphaZeroAgent] Error en NeuralPUCTMCTS: {error}")
            move = random.choice(legal_moves)

        if move not in legal_moves:
            move = random.choice(legal_moves)

        move_choice_dict["move_choice"] = move
        return move

    def choose_capture(self, state, capture_choice_dict):
        legal_moves = list(state.legal_moves(self.agent_number))
        capture_moves = [move for move in legal_moves if move[0] == "capture"]

        if not capture_moves:
            capture_choice_dict["capture_choice"] = None
            return None

        try:
            move, _ = self.mcts.search_capture(state, return_policy=True)
        except Exception as error:
            print(f"[AlphaZeroAgent] Error en captura: {error}")
            move = random.choice(capture_moves)

        if move not in capture_moves:
            move = random.choice(capture_moves)

        capture_choice_dict["capture_choice"] = move[2]
        return move[2]