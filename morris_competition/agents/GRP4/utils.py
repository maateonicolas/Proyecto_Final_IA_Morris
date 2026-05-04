from game_engine import GameState
import pickle
from typing import Dict
from pathlib import Path
from time import sleep


DB_PATH = "mcts_data.pkl"

def load_or_create(path: str = DB_PATH) -> Dict[str, Dict[str, float]]:
    """Load dict from pickle, or return {} if it doesn't exist."""
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        if not isinstance(data, dict):
            raise TypeError(f"{path} does not contain a dict")
        return data
    except FileNotFoundError:
        return {}

def call_load_file():
    here = Path(__file__).parent
    file_path = here/ "mcts_data.pkl"
    sleep(2)
    return load_or_create(file_path)

# def state_key(state: GameState) -> str:
#     """
#     Key format: '24digits_cur_phase_inhand1_inhand2'
#     Example: '110020000000000000000000_1_placing_3_4'
#     """
#     board_str = ''.join(str(v) for v in state.board)
#     return f"{board_str}_{state.cur}_{state.phase}_{state.in_hand[1]}_{state.in_hand[2]}"
