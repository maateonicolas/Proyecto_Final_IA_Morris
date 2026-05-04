import sys
from pathlib import Path


def test_az_checkpoint_can_be_loaded_if_exists():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from training.evaluate_az_model import CHECKPOINT_PATH, load_az_checkpoint

    if not CHECKPOINT_PATH.exists():
        return

    model, checkpoint = load_az_checkpoint()

    assert model is not None
    assert "model_state_dict" in checkpoint
    assert checkpoint["input_size"] == 80
    assert checkpoint["action_size"] == 624
    assert checkpoint["dataset_type"] == "alphazero_visit_policy"