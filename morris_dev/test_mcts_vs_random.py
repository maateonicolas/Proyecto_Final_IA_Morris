# test_mcts_vs_random.py
#
# Prueba automática: MCTSAgent vs RandomAgent sin interfaz gráfica.
#
# Estructura:
#   - Serie 1: MCTS como Player 1,  Random como Player 2
#   - Serie 2: Random como Player 1, MCTS como Player 2
#
# Propósito: verificar que MCTS supera estadísticamente a un agente aleatorio.
# Usado para la sección de resultados de la presentación universitaria.

import random
import time
import sys

from game_engine import GameState
from agents.mcts_agent import MCTSAgent


# -----------------------------------------------------------------------
# Agente aleatorio de referencia (baseline)
# -----------------------------------------------------------------------

class RandomAgent:
    """
    Agente baseline que siempre elige un movimiento legal al azar.
    Se usa como punto de comparación para medir la mejora de MCTS.
    """

    def __init__(self, agent_num, name="Random"):
        self.agent_number = agent_num
        self.name = name
        self.number_of_wins = 0

    def choose_move(self, state, move_choice_dict):
        """Elige un movimiento legal aleatorio."""
        moves = state.legal_moves(self.agent_number)
        if moves:
            move_choice_dict["move_choice"] = random.choice(moves)

    def choose_capture(self, state, capture_choice_dict):
        """Elige una captura legal aleatoria."""
        moves = state.legal_moves(self.agent_number)
        if moves:
            capture_choice_dict["capture_choice"] = random.choice(moves)[2]


# -----------------------------------------------------------------------
# Motor de partida sin interfaz gráfica
# -----------------------------------------------------------------------

def play_game(agent1, agent2, max_turns=300):
    """
    Simula una partida completa entre agent1 (Player 1) y agent2 (Player 2)
    sin ninguna interfaz gráfica.

    Parámetros
    ----------
    agent1    : agente con agent_number=1
    agent2    : agente con agent_number=2
    max_turns : límite de turnos para evitar partidas infinitas (ciclos)

    Retorna
    -------
    1    si ganó Player 1
    2    si ganó Player 2
    None si se alcanzó el límite de turnos sin ganador
    """
    state = GameState()
    agents = {1: agent1, 2: agent2}

    for turn in range(max_turns):

        # Verificar si la partida ya terminó
        if state.is_terminal():
            break

        cur_agent = agents[state.cur]

        # ---- Turno de captura obligatoria ----
        # Ocurre justo después de que un jugador forma un molino.
        # El mismo jugador debe capturar una pieza del oponente.
        if state.need_capture:
            cap_dict = {"capture_choice": None}
            # El agente recibe una COPIA del estado para no modificarlo directamente
            cur_agent.choose_capture(state.copy(), cap_dict)
            cap = cap_dict["capture_choice"]

            # Fallback si el agente no eligió nada
            if cap is None:
                legal = state.legal_moves(state.cur)
                cap = random.choice(legal)[2] if legal else None

            if cap is not None:
                state.apply_capture(cap)

        # ---- Turno de movimiento normal ----
        else:
            move_dict = {"move_choice": None}
            # El agente recibe una COPIA del estado
            cur_agent.choose_move(state.copy(), move_dict)
            move = move_dict["move_choice"]

            # Fallback si el agente no eligió nada
            if move is None:
                legal = state.legal_moves(state.cur)
                move = random.choice(legal) if legal else None

            if move is not None:
                # apply_move retorna (need_capture, src, dst)
                # Si need_capture=True, el siguiente turno del bucle lo manejará
                state.apply_move(move)

    return state.winner()


# -----------------------------------------------------------------------
# Ejecución de una serie de partidas
# -----------------------------------------------------------------------

def run_series(agent1, agent2, n_games, series_name, mcts_player_num):
    """
    Corre n_games partidas con agent1=Player1, agent2=Player2.

    mcts_player_num indica qué número de jugador es el MCTS
    para llevar el conteo correcto de victorias.

    Retorna (mcts_wins, random_wins, draws).
    """
    mcts_wins  = 0
    rand_wins  = 0
    draws      = 0

    print(f"\n{series_name}")
    print("-" * 55)

    for i in range(n_games):
        t0     = time.time()
        winner = play_game(agent1, agent2, max_turns=300)
        elapsed = time.time() - t0

        if winner == mcts_player_num:
            mcts_wins += 1
            tag = "MCTS gana  ✓"
        elif winner is not None:
            rand_wins += 1
            tag = "Random gana"
        else:
            draws += 1
            tag = "Sin ganador (límite de turnos)"

        print(f"  Partida {i + 1:2d}: {tag}   ({elapsed:.1f}s)")

    return mcts_wins, rand_wins, draws


# -----------------------------------------------------------------------
# Punto de entrada principal
# -----------------------------------------------------------------------

def main():
    # ------------------------------------------------------------------
    # Configuración del experimento
    # ------------------------------------------------------------------
    N_GAMES    = 10     # partidas por serie (5 con MCTS como P1, 10 como P2)
    TIME_LIMIT = 0.2    # segundos de búsqueda MCTS por movimiento
                        # (más alto → más fuerte pero más lento)

    print("=" * 55)
    print("  MCTS vs Random — prueba automática")
    print("=" * 55)
    print(f"\nPartidas por serie : {N_GAMES}")
    print(f"Tiempo MCTS/turno  : {TIME_LIMIT}s")
    print("\nCreando agentes...")
    print("(call_load_file tiene un sleep de 2s por agente, es normal)")

    # ------------------------------------------------------------------
    # Serie 1: MCTS como Player 1 vs Random como Player 2
    # ------------------------------------------------------------------
    mcts_p1 = MCTSAgent(1, name="MCTS-P1")
    mcts_p1.time_limit = TIME_LIMIT     # reducir para que la prueba no tarde
    rand_p2 = RandomAgent(2, name="Random-P2")

    w1, l1, d1 = run_series(
        mcts_p1, rand_p2,
        n_games     = N_GAMES,
        series_name = "Serie 1: MCTS(P1) vs Random(P2)",
        mcts_player_num = 1,
    )

    # ------------------------------------------------------------------
    # Serie 2: Random como Player 1 vs MCTS como Player 2
    # ------------------------------------------------------------------
    rand_p1 = RandomAgent(1, name="Random-P1")
    mcts_p2 = MCTSAgent(2, name="MCTS-P2")
    mcts_p2.time_limit = TIME_LIMIT

    w2, l2, d2 = run_series(
        rand_p1, mcts_p2,
        n_games     = N_GAMES,
        series_name = "Serie 2: Random(P1) vs MCTS(P2)",
        mcts_player_num = 2,
    )

    # ------------------------------------------------------------------
    # Resumen global
    # ------------------------------------------------------------------
    total_games  = 2 * N_GAMES
    total_mcts   = w1 + w2
    total_random = l1 + l2
    total_draws  = d1 + d2
    win_pct      = 100.0 * total_mcts / total_games if total_games > 0 else 0.0

    print("\n" + "=" * 55)
    print("  RESUMEN FINAL")
    print("=" * 55)
    print(f"  Total de partidas       : {total_games}")
    print(f"  Victorias de MCTS       : {total_mcts:3d}  ({win_pct:.1f}%)")
    print(f"  Victorias de Random     : {total_random:3d}  ({100.0 * total_random / total_games:.1f}%)")
    print(f"  Empates / sin ganador   : {total_draws:3d}")
    print()
    print(f"  Serie 1 (MCTS como P1) : {w1}W / {l1}L / {d1}D")
    print(f"  Serie 2 (MCTS como P2) : {w2}W / {l2}L / {d2}D")
    print()

    if win_pct > 55:
        print("  Conclusión: MCTS supera claramente al agente aleatorio.")
    elif win_pct >= 45:
        print("  Conclusión: resultados cercanos al 50%. Prueba con más")
        print("  partidas o aumenta TIME_LIMIT para ver diferencia mayor.")
    else:
        print("  Conclusión: MCTS no superó a Random en esta muestra.")
        print("  Intenta aumentar TIME_LIMIT o N_GAMES.")

    print("=" * 55)


if __name__ == "__main__":
    main()
