import sys
from pathlib import Path


def test_training_dataset_can_be_loaded():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from training.self_play import generate_self_play_dataset
    from training.train import MorrisSelfPlayDataset, DATASET_PATH

    generate_self_play_dataset(num_games=1)

    dataset = MorrisSelfPlayDataset(DATASET_PATH)

    assert len(dataset) > 0

    state, policy_target, value = dataset[0]

    assert state.shape[0] == 80
    assert 0 <= int(policy_target) < 624
    assert value.shape[0] == 1
    assert float(value.item()) in (-1.0, 0.0, 1.0)