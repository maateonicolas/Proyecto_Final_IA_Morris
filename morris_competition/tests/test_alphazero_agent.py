import sys
from pathlib import Path


def test_alphazero_agent_returns_legal_move():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from game_engine import GameState
    from agents.GRP1.alphazero_agent import AlphaZeroAgent

    state = GameState()
    agent = AlphaZeroAgent(1, simulations=5)

    move_choice_dict = {}
    agent.choose_move(state, move_choice_dict)

    assert "move_choice" in move_choice_dict
    assert move_choice_dict["move_choice"] in state.legal_moves(1)