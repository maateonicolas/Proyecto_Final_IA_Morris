# pygame_ui.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

import pygame
import sys
import time
import threading

from game_engine import GameState, opponent
from agents.mcts_agent import MCTSAgent
from agents.human_agent import HumanAgent

# ---------------- UI constants ----------------
WIDTH, HEIGHT = 800, 800
BG_COLOR = (245, 245, 245)
LINE_COLOR = (40, 40, 40)
MOVING_PIECE_LINE_COLOR = (135, 206, 235)
TEXT_COLOR = (20, 20, 20)
P1_COLOR = (30, 120, 215)
P2_COLOR = (220, 50, 50)
HILITE_COLOR = (30, 180, 120)
SELECT_COLOR = (255, 170, 30)
MILL_GLOW = (255, 210, 0)
HILITE_PIECE_TAKEN = (88, 60, 28)

RADIUS = 18
SELECT_RADIUS = 24
FONT_SIZE = 22

GRID = {
    0: (0, 0), 1: (3, 0), 2: (6, 0),
    3: (1, 1), 4: (3, 1), 5: (5, 1),
    6: (2, 2), 7: (3, 2), 8: (4, 2),
    9: (0, 3), 10: (1, 3), 11: (2, 3), 12: (4, 3), 13: (5, 3), 14: (6, 3),
    15: (2, 4), 16: (3, 4), 17: (4, 4),
    18: (1, 5), 19: (3, 5), 20: (5, 5),
    21: (0, 6), 22: (3, 6), 23: (6, 6),
}

MARGIN = 160
CELL = (WIDTH - 2 * MARGIN) // 6
POINTS = {i: (MARGIN + cx * CELL, MARGIN + cy * CELL) for i, (cx, cy) in GRID.items()}


# ---------------- Drawing ----------------
def draw_board_lines(screen, src=None, dst=None):
    # default colors
    color_h_003 = color_h_036 = LINE_COLOR    # 0-1, 1-2
    color_h_113 = color_h_135 = LINE_COLOR    # 3-4, 4-5
    color_h_223 = color_h_234 = LINE_COLOR    # 6-7, 7-8
    color_h_301 = color_h_312 = LINE_COLOR    # 9-10, 10-11
    color_h_345 = color_h_356 = LINE_COLOR    # 12-13, 13-14
    color_h_423 = color_h_434 = LINE_COLOR    # 15-16, 16-17
    color_h_513 = color_h_535 = LINE_COLOR    # 18-19, 19-20
    color_h_603 = color_h_636 = LINE_COLOR    # 21-22, 22-23

    color_v_003 = color_v_036 = LINE_COLOR    # 0-9, 9-21
    color_v_113 = color_v_135 = LINE_COLOR    # 3-10, 10-18
    color_v_223 = color_v_234 = LINE_COLOR    # 6-11, 11-15
    color_v_301 = color_v_312 = LINE_COLOR    # 1-4, 4-7
    color_v_345 = color_v_356 = LINE_COLOR    # 16-19, 19-22
    color_v_423 = color_v_434 = LINE_COLOR    # 8-12, 12-17
    color_v_513 = color_v_535 = LINE_COLOR    # 5-13, 13-20
    color_v_603 = color_v_636 = LINE_COLOR    # 2-14, 14-23

    if src is not None and dst is not None:
        # horizontals
        if (src in (0, 1)) and (dst in (0, 1)):
            color_h_003 = MOVING_PIECE_LINE_COLOR
        if (src in (1, 2)) and (dst in (1, 2)):
            color_h_036 = MOVING_PIECE_LINE_COLOR
        if (src in (3, 4)) and (dst in (3, 4)):
            color_h_113 = MOVING_PIECE_LINE_COLOR
        if (src in (4, 5)) and (dst in (4, 5)):
            color_h_135 = MOVING_PIECE_LINE_COLOR
        if (src in (6, 7)) and (dst in (6, 7)):
            color_h_223 = MOVING_PIECE_LINE_COLOR
        if (src in (7, 8)) and (dst in (7, 8)):
            color_h_234 = MOVING_PIECE_LINE_COLOR
        if (src in (9, 10)) and (dst in (9, 10)):
            color_h_301 = MOVING_PIECE_LINE_COLOR
        if (src in (10, 11)) and (dst in (10, 11)):
            color_h_312 = MOVING_PIECE_LINE_COLOR
        if (src in (12, 13)) and (dst in (12, 13)):
            color_h_345 = MOVING_PIECE_LINE_COLOR
        if (src in (13, 14)) and (dst in (13, 14)):
            color_h_356 = MOVING_PIECE_LINE_COLOR
        if (src in (15, 16)) and (dst in (15, 16)):
            color_h_423 = MOVING_PIECE_LINE_COLOR
        if (src in (16, 17)) and (dst in (16, 17)):
            color_h_434 = MOVING_PIECE_LINE_COLOR
        if (src in (18, 19)) and (dst in (18, 19)):
            color_h_513 = MOVING_PIECE_LINE_COLOR
        if (src in (19, 20)) and (dst in (19, 20)):
            color_h_535 = MOVING_PIECE_LINE_COLOR
        if (src in (21, 22)) and (dst in (21, 22)):
            color_h_603 = MOVING_PIECE_LINE_COLOR
        if (src in (22, 23)) and (dst in (22, 23)):
            color_h_636 = MOVING_PIECE_LINE_COLOR

        # verticals
        if (src in (0, 9)) and (dst in (0, 9)):
            color_v_003 = MOVING_PIECE_LINE_COLOR
        if (src in (9, 21)) and (dst in (9, 21)):
            color_v_036 = MOVING_PIECE_LINE_COLOR
        if (src in (3, 10)) and (dst in (3, 10)):
            color_v_113 = MOVING_PIECE_LINE_COLOR
        if (src in (10, 18)) and (dst in (10, 18)):
            color_v_135 = MOVING_PIECE_LINE_COLOR
        if (src in (6, 11)) and (dst in (6, 11)):
            color_v_223 = MOVING_PIECE_LINE_COLOR
        if (src in (11, 15)) and (dst in (11, 15)):
            color_v_234 = MOVING_PIECE_LINE_COLOR
        if (src in (1, 4)) and (dst in (1, 4)):
            color_v_301 = MOVING_PIECE_LINE_COLOR
        if (src in (4, 7)) and (dst in (4, 7)):
            color_v_312 = MOVING_PIECE_LINE_COLOR
        if (src in (16, 19)) and (dst in (16, 19)):
            color_v_345 = MOVING_PIECE_LINE_COLOR
        if (src in (19, 22)) and (dst in (19, 22)):
            color_v_356 = MOVING_PIECE_LINE_COLOR
        if (src in (8, 12)) and (dst in (8, 12)):
            color_v_423 = MOVING_PIECE_LINE_COLOR
        if (src in (12, 17)) and (dst in (12, 17)):
            color_v_434 = MOVING_PIECE_LINE_COLOR
        if (src in (5, 13)) and (dst in (5, 13)):
            color_v_513 = MOVING_PIECE_LINE_COLOR
        if (src in (13, 20)) and (dst in (13, 20)):
            color_v_535 = MOVING_PIECE_LINE_COLOR
        if (src in (2, 14)) and (dst in (2, 14)):
            color_v_603 = MOVING_PIECE_LINE_COLOR
        if (src in (14, 23)) and (dst in (14, 23)):
            color_v_636 = MOVING_PIECE_LINE_COLOR

    def px(c):
        return MARGIN + c * CELL

    def H(y, x1, x2, color):
        pygame.draw.line(screen, color, (px(x1), px(y)), (px(x2), px(y)), 4)

    def V(x, y1, y2, color):
        pygame.draw.line(screen, color, (px(x), px(y1)), (px(x), px(y2)), 4)

    H(0, 0, 3, color_h_003)
    H(0, 3, 6, color_h_036)
    H(1, 1, 3, color_h_113)
    H(1, 3, 5, color_h_135)
    H(2, 2, 3, color_h_223)
    H(2, 3, 4, color_h_234)
    H(3, 0, 1, color_h_301)
    H(3, 1, 2, color_h_312)
    H(3, 4, 5, color_h_345)
    H(3, 5, 6, color_h_356)
    H(4, 2, 3, color_h_423)
    H(4, 3, 4, color_h_434)
    H(5, 1, 3, color_h_513)
    H(5, 3, 5, color_h_535)
    H(6, 0, 3, color_h_603)
    H(6, 3, 6, color_h_636)

    V(0, 0, 3, color_v_003)
    V(0, 3, 6, color_v_036)
    V(1, 1, 3, color_v_113)
    V(1, 3, 5, color_v_135)
    V(2, 2, 3, color_v_223)
    V(2, 3, 4, color_v_234)
    V(3, 0, 1, color_v_301)
    V(3, 1, 2, color_v_312)
    V(3, 4, 5, color_v_345)
    V(3, 5, 6, color_v_356)
    V(4, 2, 3, color_v_423)
    V(4, 3, 4, color_v_434)
    V(5, 1, 3, color_v_513)
    V(5, 3, 5, color_v_535)
    V(6, 0, 3, color_v_603)
    V(6, 3, 6, color_v_636)


def draw_pieces(screen, state, selected=None, cap=None, src=None, dst=None):
    for i, (x, y) in POINTS.items():
        pygame.draw.circle(screen, LINE_COLOR, (x, y), 6)

        # mill glow during capture
        if state.last_mill_trip and i in state.last_mill_trip and state.need_capture:
            pygame.draw.circle(screen, MILL_GLOW, (x, y), SELECT_RADIUS + 6, 4)

        # highlight captured piece
        if cap is not None and cap == i:
            pygame.draw.circle(screen, HILITE_PIECE_TAKEN, (x, y), SELECT_RADIUS + 6, 4)

        # highlight destination when src is None (last move endpoint)
        if src is None and dst is not None and i == dst:
            pygame.draw.circle(screen, HILITE_COLOR, (x, y), SELECT_RADIUS, 3)

        if state.board[i] == 1:
            pygame.draw.circle(screen, P1_COLOR, (x, y), RADIUS)
        if selected == i:
            pygame.draw.circle(screen, SELECT_COLOR, (x, y), SELECT_RADIUS, 4)
        elif state.board[i] == 2:
            pygame.draw.circle(screen, P2_COLOR, (x, y), RADIUS)


def pos_at_mouse(mx, my):
    for i, (x, y) in POINTS.items():
        if (mx - x) ** 2 + (my - y) ** 2 <= (SELECT_RADIUS + 6) ** 2:
            return i
    return None


def draw_texts(screen, font, big_font, lines):
    y = 12
    for i, line in enumerate(lines):
        render_font = big_font if i == 0 or i == 1 else font
        render = render_font.render(line, True, TEXT_COLOR)
        screen.blit(render, (20, y))
        y += 28 if i == 0 else 22


# ---------------- Agents / Modes ----------------
def load_agents(mode="ai_vs_ai"):
    """
    mode options:
      'human_vs_ai', 'human_vs_smart_ai', 'smart_ai_vs_human',
    Uses global `state` exactly as your original code.
    """
    global agents

    if mode == "ai_vs_ai":
        agents = {
            1: MCTSAgent( 1, name="MCTS-P1"),
            2: MCTSAgent( 2, name="MCTS-P2"),
        }

    elif mode == "human_vs_ai":
        agents = {
            1: HumanAgent(1, name="Human-P1"),
            2: MCTSAgent(2, name="MCTS-P2"),
        }


def write_scores_to_file(filename, agents, game_num):
    """
    Append the current cumulative scores of all agents to a text file.
    """
    with open(filename, "a") as f:
        f.write(f"Game {game_num} results:\n")
        for p in (1, 2):
            a = agents[p]
            f.write(f"  Player {p} ({a.name}): {a.number_of_wins} wins\n")
        f.write("\n")



agents = None
state = None
winner = None


def main():
    global state, winner
    TOTAL_GAMES_TO_PLAY = 3
    game_num = 1
    state = GameState()
    another_game = True

    # Select mode here:
    #mode = "human_vs_ai"
    mode = "ai_vs_ai"

    # Load agents in background
    load_thread = threading.Thread(target=load_agents, args=(mode,))
    load_thread.daemon = True
    load_thread.start()
    loading = True

    while another_game:
        if game_num > TOTAL_GAMES_TO_PLAY:
            break
        pygame.init()
        pygame.display.set_caption("Nine Men's Morris")
        screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, FONT_SIZE)
        big_font = pygame.font.SysFont(None, 28)

        running = True
        selected = None
        human_cap = None
        cooldown = 0.1
        last_click = 0


        cap = None
        src = None
        dst = None
        human_src = None
        human_dst = None
        ai_cap = None
        ai_src = None
        ai_dst = None

        move_choice = None
        capture_choice = None
        agent_move_choice = {"move_choice": move_choice}
        agent_capture_choice = {"capture_choice": capture_choice}

        MIN_CHOOSE_TIME = 2.0
        MIN_TRIPLICATE_TIME = 0.8
        FRAME_RATE = 60
        TIME_DELAY_BETWEEN_GAMES = 1.0

        # Non-blocking AI state
        ai_move_thread = None
        ai_capture_thread = None
        ai_thinking_move = False
        ai_move_ready = False
        ai_move_decision_time = None
        pending_move = None

        ai_thinking_capture = False
        ai_capture_ready = False
        ai_capture_decision_time = None
        pending_capture = None

        while running:
            # if still loading agents, show loading screen but handle QUIT
            if loading:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                screen.fill(BG_COLOR)
                lines = ["The files of both players are presently being loaded. Please wait..."]
                draw_texts(screen, font, big_font, lines)
                draw_board_lines(screen, src, dst)
                draw_pieces(screen, state, selected, cap, src, dst)
                pygame.display.flip()

                if not load_thread.is_alive():
                    loading = False
                clock.tick(FRAME_RATE)
                continue

            # Determine winner if terminal
            winner = state.winner() if state.is_terminal() else None
            cur_agent = agents[state.cur]

            # --- Event handling (QUIT always handled) ---
            #if not winner:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    another_game = False

                # Human input only if it's a human turn
                if isinstance(cur_agent, HumanAgent) and event.type == pygame.MOUSEBUTTONDOWN:
                    ai_cap = None
                    ai_src = None
                    ai_dst = None
                    now = time.time()
                    if now - last_click <= cooldown:
                        continue
                    last_click = now
                    clicked = pos_at_mouse(*event.pos)
                    if clicked is None:
                        continue
                    print(clicked)

                    if state.need_capture:
                        # Click opponent piece to capture
                        if state.board[clicked] == opponent(state.cur):
                            state.apply_capture(clicked)
                            human_cap = clicked

                    elif state.phase == "placing":
                        # Click empty spot to place piece
                        human_cap = None
                        if state.board[clicked] == 0:
                            need_cap, human_src, human_dst = state.apply_move(
                                ("place", None, clicked)
                            )
                            if need_cap:
                                state.need_capture = True

                    else:
                        # Movement phase
                        human_cap = None
                        if selected is None and state.board[clicked] == state.cur:
                            selected = clicked
                            state.mid_move = True
                            human_src = clicked
                        elif selected is not None:
                            need_cap, human_src, human_dst = state.apply_move(
                                ("move", selected, clicked)
                            )
                            selected = None
                            if need_cap:
                                state.need_capture = True

            # --- AI logic (non-blocking) ---
            if not winner and isinstance(cur_agent, HumanAgent):
                # Human turn: AI state is idle this frame
                pass

            elif not winner and not isinstance(cur_agent, HumanAgent):
                # reset human visuals while AI is thinking/play
                human_cap = None
                human_src = None
                human_dst = None
                selected = None

                # CAPTURE phase for AI
                if state.need_capture:
                    # First priority: if capture already ready, apply it after min delay
                    if ai_capture_ready:
                        if time.time() - ai_capture_decision_time >= MIN_CHOOSE_TIME:
                            ai_cap = pending_capture
                            if ai_cap is not None:
                                state.apply_capture(ai_cap)
                            ai_capture_ready = False
                            pending_capture = None
                            ai_cap = None
                    else:
                        # if we are not already thinking, start capture thread
                        if not ai_thinking_capture:
                            agent_capture_choice["capture_choice"] = None
                            ai_capture_thread = threading.Thread(
                                target=cur_agent.choose_capture,
                                args=(state.copy(), agent_capture_choice),
                            )
                            ai_capture_thread.daemon = True
                            ai_capture_thread.start()
                            ai_thinking_capture = True
                        else:
                            # we are thinking; check if finished
                            if not ai_capture_thread.is_alive():
                                ai_capture_thread.join()
                                pending_capture = agent_capture_choice["capture_choice"]
                                ai_cap = pending_capture
                                ai_capture_decision_time = time.time()
                                ai_capture_ready = True
                                ai_thinking_capture = False

                # MOVE phase for AI
                else:
                    if ai_move_ready:
                        # We have a move result, enforce min time before applying
                        if time.time() - ai_move_decision_time >= MIN_CHOOSE_TIME:
                            move = pending_move
                            pending_move = None
                            ai_move_ready = False

                            if move is None:
                                winner = state.winner()
                            else:
                                need_cap, ai_src, ai_dst = state.apply_move(move)
                                if need_cap:
                                    # capture will be handled in next frames
                                    pass
                    else:
                        # no ready move: either start thinking or check ongoing thread
                        if not ai_thinking_move:
                            agent_move_choice["move_choice"] = None
                            ai_move_thread = threading.Thread(
                                target=cur_agent.choose_move,
                                args=(state.copy(), agent_move_choice),
                            )
                            ai_move_thread.daemon = True
                            ai_move_thread.start()
                            ai_thinking_move = True
                        else:
                            if not ai_move_thread.is_alive():
                                ai_move_thread.join()
                                pending_move = agent_move_choice["move_choice"]
                                ai_move_decision_time = time.time()
                                ai_move_ready = True
                                ai_thinking_move = False

            # --- Build text lines ---
            lines = []
            if winner:
                agents[winner].number_of_wins += 1
                win = "win!" if agents[winner].number_of_wins == 1 else "wins!"
                lines.append(f"Player {winner} {agents[winner].name}) {agents[winner].number_of_wins} {win}")
                lines.append("Press ESC to quit.")
                lines.append(f"Game #{game_num}")
                running = False
            else:
                lines.append(f"{f'Game #{game_num}':>75}")
                win = "win!" if agents[1].number_of_wins == 1 else "wins!"
                lines.append(f"Player 1 {agents[1].name} {agents[1].number_of_wins} {win}")
                win = "win!" if agents[2].number_of_wins == 1 else "wins!"
                lines[-1] += f"{f'Player 2 {agents[2].name} {agents[2].number_of_wins} {win}':>75}"

                if state.need_capture:
                    lines.append("")
                    lines.append(f"{f'Player {state.cur}: capture an opponent piece':>95}")
                else:
                    if state.phase == "placing":
                        lines.append("")
                        lines.append(f"{f'Placing — Player {state.cur} ({agents[state.cur].name})':>93}")
                        lines.append(f"{f'P1 in hand: {state.in_hand[1]} | P2 in hand: {state.in_hand[2]}':>95}")
                    else:
                        lines.append("")
                        fly1 = "(flying)" if state.on_board[1] == 3 else ""
                        fly2 = "(flying)" if state.on_board[2] == 3 else ""
                        lines.append(f"{f'Moving — Player {state.cur} ({agents[state.cur].name})':>95}")
                        lines.append(
                            f"{f'P1 on board: {state.on_board[1]}{fly1} | P2 on board: {state.on_board[2]}{fly2}':>100}"
                        )

            # --- Decide which src/dst/cap to show for highlighting ---
            if mode in ("ai_vs_ai", "dumb_ai_vs_dumb_ai", "smart_ai_vs_smart_ai", "smart_ai_vs_dumb_ai"):
                if state.cur in (1, 2):
                    cap = ai_cap
                    src = ai_src
                    dst = ai_dst

            elif mode in ("ai_vs_ai", "human_vs_smart_ai", "human_vs_dumb_ai"):
                if not state.need_capture and state.phase == "placing" and state.cur == 2:
                    cap = human_cap
                    src = human_src
                    dst = human_dst
                elif not state.need_capture and state.phase == "placing" and state.cur == 1:
                    cap = ai_cap
                    src = ai_src
                    dst = ai_dst
                elif state.need_capture and state.cur == 2:
                    cap = ai_cap
                    src = ai_src
                    dst = ai_dst
                elif state.need_capture and state.cur == 1:
                    cap = human_cap
                    src = human_src
                    dst = human_dst
                elif state.phase == "moving" and state.mid_move and state.cur == 1:
                    cap = human_cap
                    src = human_src
                    dst = human_dst
                elif state.phase == "moving" and (not state.mid_move) and state.cur == 1:
                    cap = ai_cap
                    src = ai_src
                    dst = ai_dst
                elif state.phase == "moving" and (not state.mid_move) and state.cur == 2:
                    cap = ai_cap
                    src = ai_src
                    dst = ai_dst

            elif mode == "human_vs_human":
                cap = human_cap
                src = human_src
                dst = human_dst

            # --- Draw frame ---
            screen.fill(BG_COLOR)
            draw_board_lines(screen, src, dst)
            draw_pieces(screen, state, selected, cap, src, dst)
            draw_texts(screen, font, big_font, lines)
            pygame.display.flip()

            # After capture highlight, keep it on screen briefly
            if cap is not None:
                #time.sleep(MIN_TRIPLICATE_TIME)
                cap = None

            clock.tick(FRAME_RATE)

        # end of single game
        pygame.quit()
        time.sleep(TIME_DELAY_BETWEEN_GAMES)
        game_num += 1
        winner = None
        state = GameState()

        # start loading new agents for next game
        # load_thread = threading.Thread(target=load_agents, args=(mode,))
        # load_thread.daemon = True
        # load_thread.start()
        # #loading = False

    pygame.quit()
    write_scores_to_file("scores.txt", agents, TOTAL_GAMES_TO_PLAY)
    sys.exit()


if __name__ == "__main__":
    main()
