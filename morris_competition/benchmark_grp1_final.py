# benchmark_grp1_final.py
#
# Benchmark final del agente GRP1 integrado en la plataforma de competencia.
#
# Objetivo:
# - Evaluar GRP1 vs GRP2 Random sin interfaz gráfica.
# - Alternar lados para evitar sesgo de primer jugador.
# - Generar datos defendibles para README, docs y presentación.

import random
import time

from game_engine import GameState
from agents.GRP1.grp1_agent import GRP1
from agents.GRP2.grp2_agent import GRP2


MAX_TURNS = 150
N_GAMES_PER_SIDE = 10


def play_game(agent1, agent2, max_turns=MAX_TURNS):
    """
    Ejecuta una partida completa sin Pygame.

    agent1 juega como Player 1.
    agent2 juega como Player 2.

    Retorna:
        1    si gana Player 1
        2    si gana Player 2
        None si no hay ganador antes de max_turns
    """
    state = GameState()
    agents = {
        1: agent1,
        2: agent2,
    }

    for _ in range(max_turns):

        if state.is_terminal():
            break

        cur_agent = agents[state.cur]

        if state.need_capture:
            capture_choice_dict = {"capture_choice": None}
            cur_agent.choose_capture(state.copy(), capture_choice_dict)

            capture = capture_choice_dict["capture_choice"]

            if capture is None:
                legal = state.legal_moves(state.cur)
                capture = random.choice(legal)[2] if legal else None

            legal_captures = [move[2] for move in state.legal_moves(state.cur)]

            if capture not in legal_captures:
                # Pierde el jugador que eligió una captura ilegal.
                return 2 if state.cur == 1 else 1

            state.apply_capture(capture)

        else:
            move_choice_dict = {"move_choice": None}
            cur_agent.choose_move(state.copy(), move_choice_dict)

            move = move_choice_dict["move_choice"]

            if move is None:
                legal = state.legal_moves(state.cur)
                move = random.choice(legal) if legal else None

            legal_moves = state.legal_moves(state.cur)

            if move not in legal_moves:
                # Pierde el jugador que eligió un movimiento ilegal.
                return 2 if state.cur == 1 else 1

            state.apply_move(move)

    return state.winner()


class Result:
    def __init__(self, name, grp1_player):
        self.name = name
        self.grp1_player = grp1_player
        self.n_games = 0
        self.grp1_wins = 0
        self.grp2_wins = 0
        self.draws = 0
        self.elapsed = 0.0

    def record(self, winner):
        self.n_games += 1

        if winner is None:
            self.draws += 1
        elif winner == self.grp1_player:
            self.grp1_wins += 1
        else:
            self.grp2_wins += 1

    @property
    def grp1_winrate(self):
        if self.n_games == 0:
            return 0.0
        return 100.0 * self.grp1_wins / self.n_games


def run_series(agent1, agent2, n_games, grp1_player, name):
    result = Result(name=name, grp1_player=grp1_player)
    symbols = []

    print(f"\n{name}")
    print("-" * 60)

    start = time.time()

    for i in range(n_games):
        winner = play_game(agent1, agent2)
        result.record(winner)

        if winner is None:
            sym = "·"
        elif winner == grp1_player:
            sym = "G"
        else:
            sym = "r"

        symbols.append(sym)

        if (i + 1) % 10 == 0 or i == n_games - 1:
            begin = (i // 10) * 10
            chunk = symbols[begin:]
            print(f"  [{begin + 1:02d}-{i + 1:02d}] {'  '.join(chunk)}")

    result.elapsed = time.time() - start

    print(
        f"  → GRP1:{result.grp1_wins}  "
        f"GRP2:{result.grp2_wins}  "
        f"D:{result.draws}  "
        f"WR-GRP1={result.grp1_winrate:.1f}%  "
        f"({result.elapsed:.1f}s)"
    )

    return result


def print_summary(r1, r2):
    total_games = r1.n_games + r2.n_games
    total_grp1 = r1.grp1_wins + r2.grp1_wins
    total_grp2 = r1.grp2_wins + r2.grp2_wins
    total_draws = r1.draws + r2.draws
    total_elapsed = r1.elapsed + r2.elapsed

    winrate = 100.0 * total_grp1 / total_games if total_games > 0 else 0.0

    print("\n" + "=" * 75)
    print("RESUMEN FINAL — GRP1 vs GRP2 Random")
    print("=" * 75)
    print(f"Total partidas       : {total_games}")
    print(f"Victorias GRP1       : {total_grp1}")
    print(f"Victorias GRP2       : {total_grp2}")
    print(f"Empates              : {total_draws}")
    print(f"Win rate GRP1        : {winrate:.1f}%")
    print(f"Tiempo total         : {total_elapsed:.1f}s")
    print("=" * 75)

    if winrate > 70:
        print("Conclusión: GRP1 supera claramente al agente aleatorio.")
    elif winrate >= 55:
        print("Conclusión: GRP1 supera al agente aleatorio con ventaja moderada.")
    elif winrate >= 45:
        print("Conclusión: rendimiento cercano a Random. Se debe revisar MCTS/fallback.")
    else:
        print("Conclusión: GRP1 no está superando al agente aleatorio en esta muestra.")


def main():
    print("=" * 75)
    print("BENCHMARK FINAL — GRP1 MCTS vs GRP2 Random")
    print("=" * 75)
    print(f"Partidas por lado: {N_GAMES_PER_SIDE}")
    print(f"MAX_TURNS        : {MAX_TURNS}")
    print("Leyenda          : G=GRP1 gana, r=GRP2 gana, ·=empate/límite")

    grp1_p1 = GRP1(1, name="GRP1")
    grp1_p2 = GRP1(2, name="GRP1")
    grp2_p1 = GRP2(1, name="GRP2")
    grp2_p2 = GRP2(2, name="GRP2")

    r1 = run_series(
        agent1=grp1_p1,
        agent2=grp2_p2,
        n_games=N_GAMES_PER_SIDE,
        grp1_player=1,
        name="Serie 1 — GRP1(P1) vs GRP2(P2)",
    )

    r2 = run_series(
        agent1=grp2_p1,
        agent2=grp1_p2,
        n_games=N_GAMES_PER_SIDE,
        grp1_player=2,
        name="Serie 2 — GRP2(P1) vs GRP1(P2)",
    )

    print_summary(r1, r2)


if __name__ == "__main__":
    main()