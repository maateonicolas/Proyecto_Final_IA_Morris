import sys
from pathlib import Path


def test_neural_model_forward_pass():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    import torch

    from game_engine import GameState
    from agents.GRP1.model import MorrisNet, INPUT_SIZE, ACTION_SIZE
    from agents.GRP1.neural_utils import encode_state, legal_action_indices

    state = GameState()
    player = 1

    encoded = encode_state(state, player)

    assert len(encoded) == INPUT_SIZE

    model = MorrisNet()

    x = torch.tensor(encoded, dtype=torch.float32).unsqueeze(0)

    policy_logits, value = model(x)

    assert policy_logits.shape == (1, ACTION_SIZE)
    assert value.shape == (1, 1)

    legal_indices = legal_action_indices(state, player)

    assert len(legal_indices) == len(state.legal_moves(player))
    assert all(0 <= idx < ACTION_SIZE for idx in legal_indices)