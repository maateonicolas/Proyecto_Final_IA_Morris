class HumanAgent:
    def __init__(self, agent_number, name="Human"):
        self.name = name
        self.agent_number = agent_number
        self.number_of_wins = 0

    def choose_move(self, state):
        return None   # mouse decides

    def choose_capture(self, state):
        return None