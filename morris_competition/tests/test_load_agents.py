import sys
from pathlib import Path


def test_load_agents_grp1_vs_grp2():
    competition_path = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(competition_path))

    from load_agents import load_agents

    out = {}
    load_agents("GRP1_vs_GRP2_12", out)

    assert "agents" in out
    assert 1 in out["agents"]
    assert 2 in out["agents"]

    assert out["agents"][1].name == "GRP1"
    assert out["agents"][2].name == "GRP2"

    assert out["agents"][1].agent_number == 1
    assert out["agents"][2].agent_number == 2