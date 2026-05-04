import sys
from pathlib import Path


def test_self_play_generates_examples():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from training.self_play import play_self_play_game

    examples = play_self_play_game(game_id=0)

    assert isinstance(examples, list)

    if len(examples) > 0:
        sample = examples[0]

        assert "state" in sample
        assert "policy" in sample
        assert "player" in sample
        assert "value" in sample

        assert len(sample["state"]) == 80
        assert len(sample["policy"]) == 624
        assert sample["player"] in (1, 2)
        assert sample["value"] in (-1.0, 0.0, 1.0)