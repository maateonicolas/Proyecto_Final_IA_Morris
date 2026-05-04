import threading

from agents.GRP1.grp1_agent import GRP1
from agents.GRP2.grp2_agent import GRP2
from agents.GRP3.grp3_agent import GRP3
from agents.GRP4.grp4_agent import GRP4
from agents.GRP5.grp5_agent import GRP5
from agents.GRP6.grp6_agent import GRP6
from agents.GRP7.grp7_agent import GRP7
from agents.GRP8.grp8_agent import GRP8

class HumanAgent:
    def __init__(self, agent_num, name="HUMAN"):
        self.agent_number = agent_num
        self.name = name
        self.number_of_wins = 0
# agents = None
mode12 = "GRP1_vs_GRP2_12"
mode21 = "GRP1_vs_GRP2_21"
mode13 = "GRP1_vs_GRP3_12"
mode31 = "GRP1_vs_GRP3_21"
mode14 = "GRP1_vs_GRP4_12"
mode41 = "GRP1_vs_GRP4_21"
mode15 = "GRP1_vs_GRP5_12"
mode51 = "GRP1_vs_GRP5_21"
mode16 = "GRP1_vs_GRP6_12"
mode61 = "GRP1_vs_GRP6_21"
mode17 = "GRP1_vs_GRP7_12"
mode71 = "GRP1_vs_GRP7_21"
mode18 = "GRP1_vs_GRP8_12"
mode81 = "GRP1_vs_GRP8_21"
mode23 = "GRP2_vs_GRP3_12"
mode32 = "GRP2_vs_GRP3_21"
mode24 = "GRP2_vs_GRP4_12"
mode42 = "GRP2_vs_GRP4_21"
mode25 = "GRP2_vs_GRP5_12"
mode52 = "GRP2_vs_GRP5_21"
mode26 = "GRP2_vs_GRP6_12"
mode62 = "GRP2_vs_GRP6_21"
mode27 = "GRP2_vs_GRP7_12"
mode72 = "GRP2_vs_GRP7_21"
mode28 = "GRP2_vs_GRP8_12"
mode82 = "GRP2_vs_GRP8_21"
mode34 = "GRP3_vs_GRP4_12"
mode43 = "GRP3_vs_GRP4_21"
mode35 = "GRP3_vs_GRP5_12"
mode53 = "GRP3_vs_GRP5_21"
mode36 = "GRP3_vs_GRP6_12"
mode63 = "GRP3_vs_GRP6_21"
mode37 = "GRP3_vs_GRP7_12"
mode73 = "GRP3_vs_GRP7_21"
mode38 = "GRP3_vs_GRP8_12"
mode83 = "GRP3_vs_GRP8_21"
mode45 = "GRP4_vs_GRP5_12"
mode54 = "GRP4_vs_GRP5_21"
mode46 = "GRP4_vs_GRP6_12"
mode64 = "GRP4_vs_GRP6_21"
mode47 = "GRP4_vs_GRP7_12"
mode74 = "GRP4_vs_GRP7_21"
mode48 = "GRP4_vs_GRP8_12"
mode84 = "GRP4_vs_GRP8_21"
mode56 = "GRP5_vs_GRP6_12"
mode65 = "GRP5_vs_GRP6_21"
mode57 = "GRP5_vs_GRP7_12"
mode75 = "GRP5_vs_GRP7_21"
mode58 = "GRP5_vs_GRP8_12"
mode85 = "GRP5_vs_GRP8_21"
mode67 = "GRP6_vs_GRP7_12"
mode76 = "GRP6_vs_GRP7_21"
mode68 = "GRP6_vs_GRP8_12"
mode86 = "GRP6_vs_GRP8_21"
mode78 = "GRP7_vs_GRP8_12"
mode87 = "GRP7_vs_GRP8_21"
moderr = "RAND_vs_RAND"
modehai = "H_vs_AI"

AGENTS_READY = threading.Event()


def load_agents(mode, out):
    """
    mode options:

    """
    # global agents
    global AGENTS_READY

    if mode == "HUMAN_vs_GRP1":
        agents = {
            1: HumanAgent(1, name="HUMAN"),
            2: GRP1(2, name="GRP1"),
        }

    elif mode == "GRP1_vs_GRP2_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP2(2, name="GRP2"),
        }
    elif mode == "GRP1_vs_GRP2_21":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP1(2, name="GRP1"),
        }

    if mode == "GRP1_vs_GRP3_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP3(2, name="GRP3"),
        }
    elif mode == "GRP1_vs_GRP3_21":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP1(2, name="GRP1"),
        }

    if mode == "GRP1_vs_GRP4_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP4(2, name="GRP4"),
        }
    elif mode == "GRP1_vs_GRP4_21":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP1(2, name="GRP1"),
        }

    if mode == "GRP1_vs_GRP5_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP5(2, name="GRP5"),
        }
    elif mode == "GRP1_vs_GRP5_21":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP1(2, name="GRP1"),
        }
    elif mode == "GRP1_vs_GRP6_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP6(2, name="GRP6"),
        }

    elif mode == "GRP1_vs_GRP6_21":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP1(2, name="GRP1"),
        }

    elif mode == "GRP1_vs_GRP7_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP7(2, name="GRP7"),
        }

    elif mode == "GRP1_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP1(2, name="GRP1"),
        }

    elif mode == "GRP1_vs_GRP8_12":
        agents = {
            1: GRP1(1, name="GRP1"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP1_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP1(2, name="GRP1"),
        }



    elif mode == "GRP2_vs_GRP3_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP3(2, name="GRP3"),
        }
    elif mode == "GRP2_vs_GRP3_21":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP2(2, name="GRP2"),
        }

    elif mode == "GRP2_vs_GRP4_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP4(2, name="GRP4"),
        }
    elif mode == "GRP2_vs_GRP4_21":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP2(2, name="GRP2"),
        }

    elif mode == "GRP2_vs_GRP5_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP5(2, name="GRP5"),
        }
    elif mode == "GRP2_vs_GRP5_21":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP2(2, name="GRP2"),
        }

    elif mode == "GRP2_vs_GRP6_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP6(2, name="GRP6"),
        }
    elif mode == "GRP2_vs_GRP6_21":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP2(2, name="GRP2"),
        }


    elif mode == "GRP2_vs_GRP7_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP7(2, name="GRP7"),
        }
    elif mode == "GRP2_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP2(2, name="GRP2"),
        }

    elif mode == "GRP2_vs_GRP8_12":
        agents = {
            1: GRP2(1, name="GRP2"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP2_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP2(2, name="GRP2"),
        }



    elif mode == "GRP3_vs_GRP4_12":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP4(2, name="GRP4"),
        }
    elif mode == "GRP3_vs_GRP4_21":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP3(2, name="GRP3"),
        }

    elif mode == "GRP3_vs_GRP5_12":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP5(2, name="GRP5"),
        }
    elif mode == "GRP3_vs_GRP5_21":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP3(2, name="GRP3"),
        }

    elif mode == "GRP3_vs_GRP6_12":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP6(2, name="GRP6"),
        }
    elif mode == "GRP3_vs_GRP6_21":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP3(2, name="GRP3"),
        }

    elif mode == "GRP3_vs_GRP7_12":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP7(2, name="GRP7"),
        }
    elif mode == "GRP3_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP3(2, name="GRP3"),
        }

    elif mode == "GRP3_vs_GRP8_12":
        agents = {
            1: GRP3(1, name="GRP3"),
            2: GRP8(2, name="GRP8"),
        }

    elif mode == "GRP3_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP3(2, name="GRP3"),
        }


    elif mode == "GRP4_vs_GRP5_12":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP5(2, name="GRP5"),
        }
    elif mode == "GRP4_vs_GRP5_21":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP4(2, name="GRP4"),
        }

    elif mode == "GRP4_vs_GRP6_12":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP6(2, name="GRP6"),
        }
    elif mode == "GRP4_vs_GRP6_21":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP4(2, name="GRP4"),
        }

    elif mode == "GRP4_vs_GRP7_12":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP7(2, name="GRP7"),
        }
    elif mode == "GRP4_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP4(2, name="GRP4"),
        }

    elif mode == "GRP4_vs_GRP8_12":
        agents = {
            1: GRP4(1, name="GRP4"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP4_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP4(2, name="GRP4"),
        }



    elif mode == "GRP5_vs_GRP6_12":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP6(2, name="GRP6"),
        }
    elif mode == "GRP5_vs_GRP6_21":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP5(2, name="GRP5"),
        }

    elif mode == "GRP5_vs_GRP7_12":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP7(2, name="GRP7"),
        }
    elif mode == "GRP5_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP5(2, name="GRP5"),
        }

    elif mode == "GRP5_vs_GRP8_12":
        agents = {
            1: GRP5(1, name="GRP5"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP5_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP5(2, name="GRP5"),
        }

    elif mode == "GRP6_vs_GRP7_12":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP7(2, name="GRP7"),
        }
    elif mode == "GRP6_vs_GRP7_21":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP6(2, name="GRP6"),
        }

    elif mode == "GRP6_vs_GRP8_12":
        agents = {
            1: GRP6(1, name="GRP6"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP6_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP6(2, name="GRP6"),
        }

    elif mode == "GRP7_vs_GRP8_12":
        agents = {
            1: GRP7(1, name="GRP7"),
            2: GRP8(2, name="GRP8"),
        }
    elif mode == "GRP7_vs_GRP8_21":
        agents = {
            1: GRP8(1, name="GRP8"),
            2: GRP7(2, name="GRP7"),
        }

    if "agents" not in locals():
        raise ValueError(f"Modo de juego no reconocido: {mode}")

    out["agents"] = agents
    AGENTS_READY.set()
