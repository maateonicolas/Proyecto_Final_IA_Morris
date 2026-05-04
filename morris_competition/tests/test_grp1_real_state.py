import sys
from pathlib import Path


def test_grp1_choose_move_with_real_initial_state():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from game_engine import GameState
    from agents.GRP1.grp1_agent import GRP1

    state = GameState()
    agent = GRP1(1, name="GRP1")

    move_choice_dict = {}
    agent.choose_move(state, move_choice_dict)

    assert "move_choice" in move_choice_dict
    assert move_choice_dict["move_choice"] in state.legal_moves(1)