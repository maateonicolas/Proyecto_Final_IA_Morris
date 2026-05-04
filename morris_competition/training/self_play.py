# training/self_play.py

import random
import pickle
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game_engine import GameState
from agents.GRP1.grp1_agent import GRP1
from agents.GRP1.neural_utils import encode_state, action_to_index, ACTION_SIZE


MAX_TURNS = 150
OUTPUT_DIR = ROOT / "training" / "data"


def one_hot_policy(action):
    """
    Crea una política objetivo simple:
    1.0 en la acción elegida por el agente.
    0.0 en las demás.

    En AlphaZero real se usaría la distribución de visitas del MCTS.
    Esta versión es una primera aproximación.
    """
    policy = [0.0] * ACTION_SIZE

    if action is not None:
        idx = action_to_index(action)
        policy[idx] = 1.0

    return policy


def play_self_play_game(game_id=0):
    """
    Genera una partida de self-play usando GRP1 contra GRP1.

    Retorna ejemplos:
    {
        "state": estado codificado,
        "policy": acción elegida como one-hot,
        "player": jugador que tomó la decisión,
        "value": resultado final desde el punto de vista del jugador
    }
    """

    state = GameState()

    agents = {
        1: GRP1(1, name="GRP1_SELF_P1"),
        2: GRP1(2, name="GRP1_SELF_P2"),
    }

    examples = []
    turn_count = 0

    while not state.is_terminal() and turn_count < MAX_TURNS:
        current_player = state.cur
        current_agent = agents[current_player]

        if state.need_capture:
            capture_dict = {"capture_choice": None}
            current_agent.choose_capture(state.copy(), capture_dict)

            capture = capture_dict["capture_choice"]

            legal_captures = [move[2] for move in state.legal_moves(current_player)]

            if capture not in legal_captures:
                break

            # Guardamos estado de captura también
            action = ("capture", None, capture)

            examples.append({
                "state": encode_state(state, current_player),
                "policy": one_hot_policy(action),
                "player": current_player,
                "value": None,
            })

            state.apply_capture(capture)

        else:
            move_dict = {"move_choice": None}
            current_agent.choose_move(state.copy(), move_dict)

            move = move_dict["move_choice"]

            legal_moves = state.legal_moves(current_player)

            if move not in legal_moves:
                break

            examples.append({
                "state": encode_state(state, current_player),
                "policy": one_hot_policy(move),
                "player": current_player,
                "value": None,
            })

            state.apply_move(move)

        turn_count += 1

    winner = state.winner()

    for ex in examples:
        if winner is None:
            ex["value"] = 0.0
        elif winner == ex["player"]:
            ex["value"] = 1.0
        else:
            ex["value"] = -1.0

    print(
        f"Self-play game {game_id}: "
        f"turns={turn_count}, winner={winner}, examples={len(examples)}"
    )

    return examples


def generate_self_play_dataset(num_games=5):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = []

    for game_id in range(1, num_games + 1):
        examples = play_self_play_game(game_id)
        dataset.extend(examples)

    output_path = OUTPUT_DIR / "self_play_dataset.pkl"

    with open(output_path, "wb") as f:
        pickle.dump(dataset, f)

    print(f"\nDataset saved to: {output_path}")
    print(f"Total examples: {len(dataset)}")

    return dataset


if __name__ == "__main__":
    generate_self_play_dataset(num_games=5)