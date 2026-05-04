import sys
from pathlib import Path


def test_neural_policy_selects_legal_action():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from game_engine import GameState
    from agents.GRP1.model import MorrisNet, predict
    from agents.GRP1.neural_utils import (
        encode_state,
        legal_action_indices,
        policy_to_legal_action,
    )

    state = GameState()
    player = 1

    model = MorrisNet()
    encoded = encode_state(state, player)
    legal_indices = legal_action_indices(state, player)

    policy_probs, value = predict(
        model=model,
        encoded_state=encoded,
        legal_action_indices=legal_indices,
    )

    action = policy_to_legal_action(policy_probs, state, player)

    assert action in state.legal_moves(player)
    assert -1.0 <= value <= 1.0