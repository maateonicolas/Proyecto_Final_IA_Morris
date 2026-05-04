import sys
from pathlib import Path


def test_trained_model_checkpoint_predicts_legal_action():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from training.self_play import generate_self_play_dataset
    from training.train import train_model
    from training.evaluate_model import evaluate_initial_state

    generate_self_play_dataset(num_games=1)
    train_model()

    action, value = evaluate_initial_state()

    assert action is not None
    assert -1.0 <= value <= 1.0