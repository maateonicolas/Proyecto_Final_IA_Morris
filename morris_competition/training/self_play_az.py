# training/self_play_az.py
#
# Self-play estilo AlphaZero.
#
# Diferencia con self_play.py:
# - self_play.py guarda una policy one-hot.
# - self_play_az.py guarda la distribución de visitas del MCTS PUCT.
#
# Cada ejemplo tiene:
# - state: vector codificado de tamaño 80
# - policy: visit_policy de tamaño 624
# - player: jugador que tomó la decisión
# - value: resultado final desde la perspectiva de ese jugador

from pathlib import Path
import pickle
import sys
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game_engine import GameState
from agents.GRP1.neural_utils import encode_state, action_to_index, ACTION_SIZE
from agents.GRP1.neural_puct_mcts import NeuralPUCTMCTS


MAX_TURNS = 150
NUM_GAMES = 10
SIMULATIONS = 40

OUTPUT_DIR = ROOT / "training" / "data"
OUTPUT_PATH = OUTPUT_DIR / "self_play_az_dataset.pkl"


def fallback_policy_for_action(action):
    """
    Crea una policy one-hot de respaldo.
    Se usa solo si algo falla en PUCT.
    """
    policy = [0.0] * ACTION_SIZE

    if action is not None:
        idx = action_to_index(action)
        policy[idx] = 1.0

    return policy


def choose_random_legal_action(state, player):
    legal_moves = list(state.legal_moves(player))

    if not legal_moves:
        return None

    return random.choice(legal_moves)


def play_self_play_az_game(game_id=1):
    """
    Juega una partida AlphaZero self-play.

    Usa NeuralPUCTMCTS para ambos jugadores.
    Guarda estados y políticas de visitas.
    """

    state = GameState()

    mcts_agents = {
        1: NeuralPUCTMCTS(
            agent_number=1,
            simulations=SIMULATIONS,
        ),
        2: NeuralPUCTMCTS(
            agent_number=2,
            simulations=SIMULATIONS,
        ),
    }

    examples = []
    turn_count = 0

    while not state.is_terminal() and turn_count < MAX_TURNS:
        current_player = state.cur
        mcts = mcts_agents[current_player]

        encoded_state = encode_state(state, current_player)

        if state.need_capture:
            legal_moves = list(state.legal_moves(current_player))
            capture_moves = [move for move in legal_moves if move[0] == "capture"]

            if not capture_moves:
                break

            try:
                move, visit_policy = mcts.search_capture(
                    state.copy(),
                    return_policy=True,
                )
            except Exception as error:
                print(f"[self_play_az] Error captura PUCT: {error}")
                move = random.choice(capture_moves)
                visit_policy = fallback_policy_for_action(move)

            if move not in capture_moves:
                move = random.choice(capture_moves)
                visit_policy = fallback_policy_for_action(move)

            examples.append({
                "state": encoded_state,
                "policy": visit_policy,
                "player": current_player,
                "value": None,
            })

            state.apply_capture(move[2])

        else:
            legal_moves = [
                move for move in state.legal_moves(current_player)
                if move[0] != "capture"
            ]

            if not legal_moves:
                break

            try:
                move, visit_policy = mcts.search(
                    state.copy(),
                    return_policy=True,
                )
            except Exception as error:
                print(f"[self_play_az] Error movimiento PUCT: {error}")
                move = random.choice(legal_moves)
                visit_policy = fallback_policy_for_action(move)

            if move not in legal_moves:
                move = random.choice(legal_moves)
                visit_policy = fallback_policy_for_action(move)

            examples.append({
                "state": encoded_state,
                "policy": visit_policy,
                "player": current_player,
                "value": None,
            })

            state.apply_move(move)

        turn_count += 1

    winner = state.winner()

    for example in examples:
        if winner is None:
            example["value"] = 0.0
        elif winner == example["player"]:
            example["value"] = 1.0
        else:
            example["value"] = -1.0

    print(
        f"AZ self-play game {game_id}: "
        f"turns={turn_count}, winner={winner}, examples={len(examples)}"
    )

    return examples


def generate_az_self_play_dataset(num_games=NUM_GAMES):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = []

    for game_id in range(1, num_games + 1):
        examples = play_self_play_az_game(game_id)
        dataset.extend(examples)

    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(dataset, f)

    print("=" * 70)
    print("AlphaZero self-play dataset generated")
    print("=" * 70)
    print(f"Games          : {num_games}")
    print(f"Total examples : {len(dataset)}")
    print(f"Output         : {OUTPUT_PATH}")
    print("=" * 70)

    return dataset


if __name__ == "__main__":
    generate_az_self_play_dataset(num_games=NUM_GAMES)