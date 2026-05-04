import sys
from pathlib import Path


def test_neural_puct_mcts_returns_legal_move_and_policy():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from game_engine import GameState
    from agents.GRP1.neural_puct_mcts import NeuralPUCTMCTS

    state = GameState()

    mcts = NeuralPUCTMCTS(
        agent_number=1,
        simulations=5,
    )

    move, visit_policy = mcts.search(state, return_policy=True)

    assert move in state.legal_moves(1)
    assert len(visit_policy) == 624
    assert abs(sum(visit_policy) - 1.0) < 1e-6