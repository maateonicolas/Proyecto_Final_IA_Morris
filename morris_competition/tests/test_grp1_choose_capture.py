import sys
from pathlib import Path


def test_grp1_choose_capture_returns_capture_position():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from agents.GRP1.grp1_agent import GRP1

    class FakeState:
        def legal_moves(self, agent_number):
            return [
                ("move", 0, 5),
                ("move", 1, 6),
                ("move", 2, 7),
            ]

    state = FakeState()
    agent = GRP1(1, name="GRP1")

    capture_choice_dict = {}
    agent.choose_capture(state, capture_choice_dict)

    assert "capture_choice" in capture_choice_dict
    assert capture_choice_dict["capture_choice"] in [5, 6, 7]