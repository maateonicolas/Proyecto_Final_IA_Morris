import sys
from pathlib import Path


def test_alpha_zero_dataset_can_be_loaded():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from training.train_az import AlphaZeroSelfPlayDataset, DATASET_PATH

    dataset = AlphaZeroSelfPlayDataset(DATASET_PATH)

    assert len(dataset) > 0

    state, policy, value = dataset[0]

    assert state.shape[0] == 80
    assert policy.shape[0] == 624
    assert value.shape[0] == 1

    policy_sum = float(policy.sum().item())
    assert abs(policy_sum - 1.0) < 1e-6

    assert float(value.item()) in (-1.0, 0.0, 1.0)