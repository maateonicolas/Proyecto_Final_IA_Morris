# ============================================================
# game/game_state.py
# Nine Men's Morris — AlphaZero-Compatible Version
# Padded action space: 100 actions total
# No recursion, no truncation, no missing methods
# ============================================================

import numpy as np

# ------------------------------------------------------------
# Morris adjacency graph (24 nodes)
# ------------------------------------------------------------
ADJACENT = {
    0: [1, 9],
    1: [0, 2, 4],
    2: [1, 14],
    3: [4, 10],
    4: [1, 3, 5, 7],
    5: [4, 13],
    6: [7, 11],
    7: [4, 6, 8],
    8: [7, 12],
    9: [0, 10, 21],
    10: [3, 9, 11, 18],
    11: [6, 10, 15],
    12: [8, 13, 17],
    13: [5, 12, 14, 20],
    14: [2, 13, 23],
    15: [11, 16],
    16: [15, 17, 19],
    17: [12, 16],
    18: [10, 19],
    19: [16, 18, 22],
    20: [13, 21],
    21: [9, 20, 22],
    22: [19, 21, 23],
    23: [14, 22]
}

# UI coordinate map
BOARD_MAP = [
    (0,3), (0,6), (3,6), (6,6), (6,3), (6,0), (3,0), (0,0),
    (1,3), (1,5), (3,5), (5,5), (5,3), (5,1), (3,1), (1,1),
    (2,3), (2,4), (3,4), (4,4), (4,3), (4,2), (3,2), (2,2)
]

# ------------------------------------------------------------
# Mill patterns
# ------------------------------------------------------------
MILLS = [
    [0,1,2],[3,4,5],[6,7,8],
    [15,16,17],[18,19,20],[21,22,23],
    [0,9,21],[3,10,18],[6,11,15],
    [1,4,7],[16,19,22],[8,12,17],
    [5,13,20],[2,14,23]
]

# ------------------------------------------------------------
# Action encoding (100 actions)
# ------------------------------------------------------------
PLACE_OFFSET = 0
PLACE_COUNT = 24

MOVE_OFFSET = 24
MOVE_COUNT = 32

FLY_OFFSET = 56
FLY_COUNT = 32

CAP_OFFSET = 88
CAP_COUNT = 12

POLICY_SIZE = 100

# ------------------------------------------------------------
# Build MOVE_LIST padded to 32 entries
# ------------------------------------------------------------
REAL_MOVES = [(s, d) for s in range(24) for d in ADJACENT[s]]
assert len(REAL_MOVES) <= 32, "MOVE_COUNT too small!"

MOVE_LIST = REAL_MOVES + [(0, 0)] * (MOVE_COUNT - len(REAL_MOVES))
assert len(MOVE_LIST) == MOVE_COUNT

# ------------------------------------------------------------
# Build FLY_LIST padded to 32 entries
# ------------------------------------------------------------
REAL_FLY = [(s, d) for s in range(24) for d in range(24) if s != d]
assert len(REAL_FLY) <= 32, "FLY_COUNT too small!"

FLY_LIST = REAL_FLY + [(0, 0)] * (FLY_COUNT - len(REAL_FLY))
assert len(FLY_LIST) == FLY_COUNT

# ============================================================
# GAMESTATE CLASS
# ============================================================
class GameState:
    def __init__(self):
        self.board = np.zeros(24, dtype=np.int8)
        self.in_hand = {1: 9, 2: 9}
        self.on_board = {1: 0, 2: 0}
        self.cur = 1
        self.phase = "placing"
        self.need_capture = False
        self.last_mill = False

    # --------------------------------------------------------
    def clone(self):
        st = GameState.__new__(GameState)
        st.board = np.array(self.board, dtype=np.int8)
        st.in_hand = {1: self.in_hand[1], 2: self.in_hand[2]}
        st.on_board = {1: self.on_board[1], 2: self.on_board[2]}
        st.cur = self.cur
        st.phase = self.phase
        st.need_capture = self.need_capture
        st.last_mill = self.last_mill
        return st

    # --------------------------------------------------------
    def forms_mill(self, pos, player):
        for trio in MILLS:
            if pos in trio:
                if all(self.board[p] == player for p in trio):
                    return True
        return False

    # --------------------------------------------------------
    def apply_capture(self, pos):
        opp = 2 if self.cur == 1 else 1
        if self.board[pos] == opp:
            self.board[pos] = 0
            self.on_board[opp] -= 1

        self.need_capture = False
        self.last_mill = False
        self.update_phase()

    # --------------------------------------------------------
    def next_state(self, action_id):
        st = self.clone()
        before_hash = st.hash()

        # ----- CAPTURE -----
        if st.need_capture:
            idx = action_id - CAP_OFFSET
            opp = 2 if st.cur == 1 else 1
            opp_positions = np.where(st.board == opp)[0]

            if 0 <= idx < len(opp_positions):
                st.apply_capture(opp_positions[idx])

            elif st.hash() == before_hash:
                st.cur = opp  # force progress
            return st

        # ----- PLACING -----
        if st.in_hand[st.cur] > 0:
            if PLACE_OFFSET <= action_id < PLACE_OFFSET + PLACE_COUNT:
                dst = action_id - PLACE_OFFSET
                if st.board[dst] == 0:
                    st.board[dst] = st.cur
                    st.in_hand[st.cur] -= 1
                    st.on_board[st.cur] += 1

                    if st.forms_mill(dst, st.cur):
                        st.need_capture = True
                        st.last_mill = True
                    else:
                        st.cur = 2 if st.cur == 1 else 1
                        st.last_mill = False

                    st.update_phase()

            if st.hash() == before_hash:
                st.cur = 2 if st.cur == 1 else 1
            return st

        # ----- MOVING -----
        if st.on_board[st.cur] > 3:
            if MOVE_OFFSET <= action_id < MOVE_OFFSET + MOVE_COUNT:
                idx = action_id - MOVE_OFFSET
                src, dst = MOVE_LIST[idx]

                if st.board[src] == st.cur and st.board[dst] == 0:
                    st.board[src] = 0
                    st.board[dst] = st.cur

                    if st.forms_mill(dst, st.cur):
                        st.need_capture = True
                        st.last_mill = True
                    else:
                        st.cur = 2 if st.cur == 1 else 1
                        st.last_mill = False

                    st.update_phase()

            if st.hash() == before_hash:
                st.cur = 2 if st.cur == 1 else 1
            return st

        # ----- FLYING -----
        if st.on_board[st.cur] == 3:
            if FLY_OFFSET <= action_id < FLY_OFFSET + FLY_COUNT:
                idx = action_id - FLY_OFFSET
                src, dst = FLY_LIST[idx]

                if st.board[src] == st.cur and st.board[dst] == 0:
                    st.board[src] = 0
                    st.board[dst] = st.cur

                    if st.forms_mill(dst, st.cur):
                        st.need_capture = True
                        st.last_mill = True
                    else:
                        st.cur = 2 if st.cur == 1 else 1
                        st.last_mill = False

                    st.update_phase()

            if st.hash() == before_hash:
                st.cur = 2 if st.cur == 1 else 1
            return st

        return st

    # --------------------------------------------------------
    def update_phase(self):
        if self.in_hand[1] > 0 or self.in_hand[2] > 0:
            self.phase = "placing"
        elif self.on_board[self.cur] == 3:
            self.phase = "flying"
        else:
            self.phase = "moving"

    # --------------------------------------------------------
    def legal_actions(self):
        legal = []

        # CAPTURE
        if self.need_capture:
            opp = 2 if self.cur == 1 else 1
            opp_positions = np.where(self.board == opp)[0]
            for i, pos in enumerate(opp_positions):
                if i < CAP_COUNT:
                    legal.append(CAP_OFFSET + i)
            return legal

        # PLACING
        if self.in_hand[self.cur] > 0:
            for p in range(24):
                if self.board[p] == 0:
                    legal.append(PLACE_OFFSET + p)
            return legal

        # MOVING
        if self.on_board[self.cur] > 3:
            for i, (s, d) in enumerate(MOVE_LIST):
                if self.board[s] == self.cur and self.board[d] == 0:
                    legal.append(MOVE_OFFSET + i)
            return legal

        # FLYING
        if self.on_board[self.cur] == 3:
            for i, (s, d) in enumerate(FLY_LIST):
                if self.board[s] == self.cur and self.board[d] == 0:
                    legal.append(FLY_OFFSET + i)
            return legal

        return legal

    # --------------------------------------------------------
    def is_terminal(self):
        if self.in_hand[1] > 0 or self.in_hand[2] > 0:
            return False

        if self.on_board[self.cur] < 3:
            return True

        if not self.need_capture and len(self.legal_actions()) == 0:
            return True

        return False

    # --------------------------------------------------------
    def winner(self):
        if not self.is_terminal():
            return None
        loser = self.cur
        return 2 if loser == 1 else 1

    # --------------------------------------------------------
    def winner_value(self):
        w = self.winner()
        if w is None:
            return 0.0
        return +1.0 if w == self.cur else -1.0

    # --------------------------------------------------------
    def to_nn_input(self):
        grid = np.zeros((18, 7, 7), dtype=np.float32)

        for i, (r, c) in enumerate(BOARD_MAP):
            if self.board[i] == 1:
                grid[0, r, c] = 1
            elif self.board[i] == 2:
                grid[1, r, c] = 1

        grid[2, :, :] = 1 if self.cur == 1 else 0
        return grid

    # --------------------------------------------------------
    def hash(self):
        return hash((
            tuple(self.board.tolist()),
            self.in_hand[1], self.in_hand[2],
            self.on_board[1], self.on_board[2],
            self.cur, self.phase, self.need_capture
        ))

    @property
    def policy_size(self):
        return 100
