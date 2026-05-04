# agents/grp3_agent.py
import random
from .utils import *

class GRP3:
    def __init__(self, agent_num, name="GRP3"):
        self.name = name
        self.number_of_wins = 0
        self.agent_number = agent_num
        self.tree = call_load_file()

    def choose_move(self, state, move_choice_dict):
        if len(state.legal_moves(self.agent_number)) == 0:
            return None
        move_choice_dict["move_choice"] = random.choice(state.legal_moves(self.agent_number))
        # TODO: implement real MCTS here


    def choose_capture(self, state, capture_choice_dict):
        choice = random.choice(state.legal_moves(self.agent_number))
        capture_choice_dict["capture_choice"] = choice[2]
