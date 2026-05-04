# game_engine.py
import copy
import threading
from typing import List, Tuple, Dict, Optional

NEIGHBORS = {
    0:[1,9], 1:[0,2,4], 2:[1,14],
    3:[4,10], 4:[1,3,5,7], 5:[4,13],
    6:[7,11], 7:[4,6,8], 8:[7,12],
    9:[0,10,21], 10:[3,9,11,18], 11:[6,10,15],
    12:[8,13,17], 13:[5,12,14,20], 14:[2,13,23],
    15:[11,16], 16:[15,17,19], 17:[12,16],
    18:[10,19], 19:[16,18,20,22], 20:[13,19],
    21:[9,22], 22:[19,21,23], 23:[14,22]
}

MILLS = [
    (0,1,2), (3,4,5), (6,7,8), (9,10,11), (12,13,14), (15,16,17), (18,19,20), (21,22,23),
    (0,9,21), (3,10,18), (6,11,15), (1,4,7), (16,19,22), (8,12,17), (5,13,20), (2,14,23)
]

def opponent(p): return 2 if p == 1 else 1

class GameState:
    """
    Canonical, UI-agnostic state.
    board: list[24] with {0 empty, 1 P1, 2 P2}
    in_hand: pieces to place remaining
    on_board: pieces physically on the board
    phase: "placing" or "moving"
    cur: current player (1 or 2)
    need_capture: if the player who just formed a mill must capture
    last_mill_trip: optional for UI glow (tuple of 3 or None)
    """
    #__slots__ = ("board", "in_hand", "on_board", "phase", "phase_before_capturing", "cur", "need_capture", "last_mill_trip")
    __slots__ = ("board", "in_hand", "on_board", "phase", "cur", "mid_move", "need_capture", "last_mill_trip")


    def __init__(self):
        self.board = [0]*24
        self.in_hand = {1:9, 2:9}
        self.on_board = {1:0, 2:0}
        self.phase = "placing"
        self.cur = 1
        self.mid_move = False
        self.need_capture = False
        self.last_mill_trip = None

    def copy(self) -> "GameState":
        s = GameState()
        s.board = self.board[:]  # copy list
        s.in_hand = {1: self.in_hand[1], 2: self.in_hand[2]}
        s.on_board = {1: self.on_board[1], 2: self.on_board[2]}
        s.phase = self.phase
        s.cur = self.cur
        self.mid_move = False
        s.need_capture = self.need_capture
        return s

    # --- queries ---
    def empty_points(self):
        return [i for i,v in enumerate(self.board) if v == 0]

    def player_positions(self, player):
        return [i for i,v in enumerate(self.board) if v == player]

    def formed_mill(self, pos, player):
        for a,b,c in MILLS:
            if pos in (a,b,c) and self.board[a]==self.board[b]==self.board[c]==player:
                return True
        return False

    def get_mill_trip(self, pos, player):
        for a,b,c in MILLS:
            if pos in (a,b,c) and self.board[a]==self.board[b]==self.board[c]==player:
                return (a,b,c)
        return None


    # def legal_actions(self) -> List[Tuple[str, Optional[int], int]]:
    #     """
    #     Returns a list of actions of the form:
    #     - ("capture", None, pos)        if need_capture is True
    #     - ("place", None, dst)          if placing phase & pieces in hand
    #     - ("move", src, dst)            otherwise (moving/flying)
    #     """
    #     if self.need_capture:
    #         return [("capture", None, pos) for pos in self.legal_captures()]
    #
    #     if self.phase == "placing" and self.in_hand[self.cur] > 0:
    #         return [("place", None, p) for p in self.empty_points()]
    #
    #     # moving / flying
    #     flying = (self.on_board[self.cur] == 3)
    #     actions = []
    #     for src in self.player_positions(self.cur):
    #         neigh = range(24) if flying else NEIGHBORS[src]
    #         for dst in neigh:
    #             if dst != src and self.board[dst] == 0:
    #                 actions.append(("move", src, dst))
    #     return actions

    def legal_moves(self, player):

        if self.phase == "placing" and self.in_hand[1] == 0 and self.in_hand[2] == 0:
            self.phase = "moving"




        if self.need_capture:
            return [("capture", None, pos) for pos in self.legal_captures()]
        if self.phase == "placing":
            return [("place", None, p) for p in self.empty_points()]
        flying = (self.on_board[player] == 3)

        moves = []
        for src in self.player_positions(player):
            neigh = range(24) if flying else NEIGHBORS[src]
            for dst in neigh:
                if self.board[dst] == 0 and dst != src:
                    moves.append(("move", src, dst))
        return moves

    def legal_captures(self):
        """Return opponent pieces you can legally capture (prefer non-mill)."""
        opp = opponent(self.cur)
        opp_positions = [i for i,v in enumerate(self.board) if v == opp]
        non_mill = [p for p in opp_positions if not self._is_in_mill(p, opp)]
        return non_mill if non_mill else opp_positions

    def _is_in_mill(self, pos, player):
        for a,b,c in MILLS:
            if pos in (a,b,c) and self.board[a]==self.board[b]==self.board[c]==player:
                return True
        return False

    # --- transitions ---
    # def apply_action(self, action: Tuple[str, Optional[int], int]) -> None:
    #     """
    #     Applies an action in-place. Handles turn progression, phase changes,
    #     capture requirements, etc.
    #     """
    #     kind, src, dst = action
    #     cur = self.cur
    #
    #     if kind == "capture":
    #         # Capture is always by the player who just formed a mill (cur hasn't switched yet)
    #         self.board[dst] = 0
    #         self.on_board[opponent(cur)] -= 1
    #         self.need_capture = False
    #         self.phase = self.phase_before_capturing
    #         # After capture, pass the turn
    #         self.cur = opponent(cur)
    #         return
    #
    #     if kind == "place":
    #         self.board[dst] = cur
    #         self.in_hand[cur] -= 1
    #         self.on_board[cur] += 1
    #         mill = self.formed_mill(dst, cur)
    #         if mill:
    #             self.need_capture = True
    #             self.phase_before_capturing = self.phase
    #             self.phase = "capturing"
    #
    #             return
    #         # no mill: switch turn, possibly phase switch
    #         if self.in_hand[1] == 0 and self.in_hand[2] == 0:
    #             self.phase = "moving"
    #         self.cur = opponent(self.cur)
    #         return
    #
    #     # kind == "move"
    #     self.board[src] = 0
    #     self.board[dst] = cur
    #     mill = self.formed_mill(dst, cur)
    #     if mill:
    #         self.need_capture = True
    #         self.phase_before_capturing = self.phase
    #         self.phase = "capturing"
    #
    #         return
    #     self.cur = opponent(cur)  # normal turn handoff




    def apply_move(self, move):
        """Returns True if a capture is required (mill formed) else False."""

        kind, src, dst = move
        cur = self.cur
        mill = None
        if kind == "place":
            self.board[dst] = cur
            self.in_hand[cur] -= 1
            self.on_board[cur] += 1
            mill = self.formed_mill(dst, cur)
            self.last_mill_trip = self.get_mill_trip(dst, cur) if mill else None
        elif kind == "move":

            self.board[src] = 0
            self.board[dst] = cur
            if cur == 1:
                self.mid_move = False



            mill = self.formed_mill(dst, cur)
            self.last_mill_trip = self.get_mill_trip(dst, cur) if mill else None
        # elif kind == "capture":
        #     self.board[dst] = cur

        if self.phase == "placing" and self.in_hand[1]==0 and self.in_hand[2]==0:
            self.phase = "moving"

        if mill:
            self.need_capture = True
            return True, src, dst
        else:

            self.cur = opponent(cur)

            flying = (self.on_board[cur] == 3)
            if flying:
                src = None
            return False,src, dst

    def apply_capture(self, pos):
        opp = opponent(self.cur)
        # capture happens by the player who just formed
        # a mill (current player is unchanged until capture completes)
        self.board[pos] = 0
        self.on_board[opp] -= 1
        self.need_capture = False
        self.cur = opponent(self.cur)

    def is_terminal(self):
        # Loss if opponent has <3 pieces, or if the player to move has no moves (in moving phase)
        for p in (1,2):
            if self.on_board[p] < 3 and (self.in_hand[1]==0 and self.in_hand[2]==0):
                return True
        if self.phase == "moving":
            if not self.legal_moves(self.cur):
                return True
        return False

    def winner(self):
        # Determine winner if terminal
        if not self.is_terminal():
            return None
        for p in (1,2):
            opp = opponent(p)
            # win if opponent has <3 (and we are past placing), or opponent cannot move in moving phase
            if (self.in_hand[1]==0 and self.in_hand[2]==0 and self.on_board[opp] < 3):
                return p
            if self.phase == "moving" and not self.legal_moves(opp):
                return p
        return None

