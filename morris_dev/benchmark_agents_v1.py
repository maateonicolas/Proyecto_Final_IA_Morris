# benchmark_agents.py
#
# Benchmark completo: MCTSAgent vs RandomAgent (sin interfaz gráfica).
#
# Sección 1 — Random vs Random (20 partidas)
#   Sanity check: ¿el motor favorece artificialmente a algún jugador?
#   Esperado: ~50% victorias para cada lado.
#
# Sección 2 — MCTS vs Random (50 + 50 partidas, TIME_LIMIT = 0.2s)
#   Prueba principal de rendimiento del MCTS.
#   Se corre con MCTS como P1 y luego como P2 para eliminar sesgos.
#   Esperado: MCTS gana significativamente más del 50%.
#
# Sección 3 — Efecto del tiempo de búsqueda
#   TIME_LIMIT = 0.05 / 0.10 / 0.20 segundos.
#   20 partidas por configuración (10 como P1 + 10 como P2).
#   Esperado: mayor tiempo → mayor win rate (MCTS escala con cómputo).
#
# Resultados usados para el README y la presentación universitaria.
# Leyenda de progreso:  M = MCTS gana   r = Random gana   · = empate/límite

import random
import time

from game_engine import GameState
from agents.mcts_agent import MCTSAgent


# ═══════════════════════════════════════════════════════════════════════
# Configuración global — ajustar según tiempo disponible
# ═══════════════════════════════════════════════════════════════════════

MAX_TURNS           = 300    # tope de turnos por partida (anti-ciclo)

N_RANDOM_VS_RANDOM  = 20     # sección 1
N_MCTS_VS_RANDOM    = 50     # sección 2 (por lado → 100 total)
N_TIME_COMPARISON   = 10     # sección 3 (por lado por config → 20 total/config)

TIME_LIMITS_TO_TEST = [0.05, 0.10, 0.20]   # segundos de búsqueda MCTS/turno


# ═══════════════════════════════════════════════════════════════════════
# Agente aleatorio de referencia (baseline)
# ═══════════════════════════════════════════════════════════════════════

class RandomAgent:
    """
    Baseline: elige siempre un movimiento legal al azar.
    Sirve como punto de comparación estadística contra MCTS.
    """

    def __init__(self, agent_num, name="Random"):
        self.agent_number   = agent_num
        self.name           = name
        self.number_of_wins = 0

    def choose_move(self, state, move_choice_dict):
        moves = state.legal_moves(self.agent_number)
        if moves:
            move_choice_dict["move_choice"] = random.choice(moves)

    def choose_capture(self, state, capture_choice_dict):
        moves = state.legal_moves(self.agent_number)
        if moves:
            capture_choice_dict["capture_choice"] = random.choice(moves)[2]


# ═══════════════════════════════════════════════════════════════════════
# Motor de partida sin pygame
# ═══════════════════════════════════════════════════════════════════════

def play_game(agent1, agent2, max_turns=MAX_TURNS):
    """
    Ejecuta una partida completa entre agent1 (Player 1) y agent2 (Player 2).

    Maneja correctamente:
      - phase "placing": colocación de piezas
      - phase "moving" : movimiento y vuelo (3 piezas)
      - need_capture   : captura obligatoria tras formar molino
      - is_terminal()  : fin de partida
      - fallback aleatorio si el agente devuelve None

    Retorna:
      1    → ganó Player 1
      2    → ganó Player 2
      None → se alcanzó max_turns sin ganador (se cuenta como empate)
    """
    state  = GameState()
    agents = {1: agent1, 2: agent2}

    for _ in range(max_turns):

        if state.is_terminal():
            break

        cur = agents[state.cur]

        if state.need_capture:
            # El jugador que formó el molino debe capturar una pieza enemiga.
            d = {"capture_choice": None}
            cur.choose_capture(state.copy(), d)      # copia → el agente no altera el estado real
            cap = d["capture_choice"]
            if cap is None:                          # fallback de seguridad
                legal = state.legal_moves(state.cur)
                cap = random.choice(legal)[2] if legal else None
            if cap is not None:
                state.apply_capture(cap)
        else:
            # Movimiento normal: "place" en fase placing, "move"/"fly" en moving.
            d = {"move_choice": None}
            cur.choose_move(state.copy(), d)
            move = d["move_choice"]
            if move is None:                         # fallback de seguridad
                legal = state.legal_moves(state.cur)
                move = random.choice(legal) if legal else None
            if move is not None:
                # apply_move devuelve (need_capture, src, dst);
                # need_capture queda marcado en state, se procesa en el próximo turno.
                state.apply_move(move)

    return state.winner()


# ═══════════════════════════════════════════════════════════════════════
# Contenedor de resultados de un experimento
# ═══════════════════════════════════════════════════════════════════════

class ExpResult:
    """
    Almacena y agrega estadísticas de una serie de partidas.

    mcts_player: número de jugador que es MCTS (1 o 2),
                 o None si es Random vs Random (no hay MCTS).
    """

    def __init__(self, name, mcts_player=None):
        self.name        = name
        self.mcts_player = mcts_player   # None → sin MCTS; -1 → resultado combinado
        self.n_games     = 0
        self.p1_wins     = 0
        self.p2_wins     = 0
        self.draws       = 0
        self.mcts_wins   = 0
        self.rand_wins   = 0
        self.elapsed     = 0.0

    def record(self, winner):
        """Registra el resultado de una sola partida."""
        self.n_games += 1
        if winner == 1:
            self.p1_wins += 1
        elif winner == 2:
            self.p2_wins += 1
        else:
            self.draws += 1

        if self.mcts_player is not None:
            if winner == self.mcts_player:
                self.mcts_wins += 1
            elif winner is not None:
                self.rand_wins += 1

    @property
    def mcts_winrate(self):
        """Porcentaje de victorias de MCTS. None si no aplica."""
        if self.mcts_player is None or self.n_games == 0:
            return None
        return 100.0 * self.mcts_wins / self.n_games

    @property
    def wr_str(self):
        wr = self.mcts_winrate
        return f"{wr:5.1f}%" if wr is not None else "  N/A "

    @classmethod
    def combine(cls, name, r1, r2):
        """
        Une dos ExpResult en un resultado combinado.
        Útil para mostrar el total de una sección con dos series
        (MCTS como P1 y MCTS como P2).
        """
        c            = cls(name, mcts_player=-1)  # -1 = combinado, tiene MCTS
        c.n_games    = r1.n_games  + r2.n_games
        c.p1_wins    = r1.p1_wins  + r2.p1_wins
        c.p2_wins    = r1.p2_wins  + r2.p2_wins
        c.draws      = r1.draws    + r2.draws
        c.mcts_wins  = r1.mcts_wins + r2.mcts_wins
        c.rand_wins  = r1.rand_wins + r2.rand_wins
        c.elapsed    = r1.elapsed  + r2.elapsed
        return c


# ═══════════════════════════════════════════════════════════════════════
# Función principal de experimento
# ═══════════════════════════════════════════════════════════════════════

def run_experiment(name, agent1, agent2, n_games, mcts_player=None):
    """
    Corre n_games partidas con agent1=P1 y agent2=P2.

    Imprime el progreso compacto en grupos de 10 símbolos por línea:
      M = MCTS gana   r = Random gana   · = empate/límite
      1 = P1 gana (Random vs Random)    2 = P2 gana

    Retorna un ExpResult con todas las estadísticas.
    """
    res     = ExpResult(name, mcts_player)
    symbols = []
    t_start = time.time()

    print(f"\n  {name}")
    print(f"  {'─' * 52}")

    for i in range(n_games):
        winner = play_game(agent1, agent2)
        res.record(winner)

        # Símbolo compacto según quién ganó
        if mcts_player is not None:
            if winner == mcts_player:
                sym = "M"
            elif winner is not None:
                sym = "r"
            else:
                sym = "·"
        else:
            # Random vs Random: mostrar qué Player ganó
            sym = str(winner) if winner is not None else "·"

        symbols.append(sym)

        # Imprimir una fila cada 10 partidas o al finalizar la última
        if (i + 1) % 10 == 0 or (i + 1) == n_games:
            start = (i // 10) * 10
            chunk = symbols[start:]
            label = f"{start + 1:3d}–{i + 1:3d}"
            print(f"    [{label}]  {'  '.join(chunk)}")

    res.elapsed = time.time() - t_start

    # Línea de resumen del experimento
    mc  = str(res.mcts_wins) if mcts_player is not None else "N/A"
    rnd = str(res.rand_wins) if mcts_player is not None else "N/A"
    print(f"  → P1:{res.p1_wins}  P2:{res.p2_wins}  D:{res.draws}  "
          f"MCW:{mc}  RndW:{rnd}  WR={res.wr_str}  ({res.elapsed:.0f}s)")

    return res


# ═══════════════════════════════════════════════════════════════════════
# Tabla resumen final
# ═══════════════════════════════════════════════════════════════════════

def print_table(results, total_elapsed):
    """
    Imprime una tabla con todas las secciones del benchmark.

    Columnas:
      N     = número de partidas
      P1W   = victorias Player 1
      P2W   = victorias Player 2
      D     = empates / sin ganador
      MCW   = victorias MCTS
      RndW  = victorias Random
      WR%   = win rate de MCTS
      t(s)  = tiempo de ejecución del experimento
    """
    C = 44   # ancho de la columna de nombre

    print("\n")
    print("═" * 88)
    print(f"  {'TABLA RESUMEN — BENCHMARK NINE MEN\'S MORRIS':^86}")
    print("═" * 88)
    hdr = (f"  {'Experimento':<{C}}"
           f"  {'N':>4}  {'P1W':>4}  {'P2W':>4}  {'D':>3}"
           f"  {'MCW':>4}  {'RndW':>4}  {'WR-MCTS':>8}  {'t(s)':>6}")
    print(hdr)
    print("  " + "─" * 86)

    for r in results:
        has_mcts = r.mcts_player is not None
        mc  = f"{r.mcts_wins:>4}" if has_mcts else " N/A"
        rnd = f"{r.rand_wins:>4}" if has_mcts else " N/A"
        print(
            f"  {r.name:<{C}}"
            f"  {r.n_games:>4}  {r.p1_wins:>4}  {r.p2_wins:>4}  {r.draws:>3}"
            f"  {mc}  {rnd}  {r.wr_str:>8}  {r.elapsed:>6.0f}"
        )

    print("═" * 88)
    print(f"  Tiempo total de benchmark: {total_elapsed:.0f}s  "
          f"({total_elapsed / 60:.1f} min)")
    print("═" * 88)


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    t_benchmark_start = time.time()

    print("═" * 60)
    print("  BENCHMARK — Nine Men's Morris")
    print("  MCTS básico vs Agente aleatorio")
    print("═" * 60)
    print(f"\n  MAX_TURNS           : {MAX_TURNS} turnos/partida (anti-ciclo)")
    print(f"  Sección 1           : {N_RANDOM_VS_RANDOM} partidas  (Random vs Random)")
    print(f"  Sección 2           : {N_MCTS_VS_RANDOM}+{N_MCTS_VS_RANDOM} partidas  (MCTS vs Random, TL=0.2s)")
    print(f"  Sección 3           : {N_TIME_COMPARISON}+{N_TIME_COMPARISON} partidas/config  (TL = {TIME_LIMITS_TO_TEST})")
    total_est = (N_MCTS_VS_RANDOM * 2 + N_TIME_COMPARISON * 2 * len(TIME_LIMITS_TO_TEST)) * 0.2 * 30
    print(f"  Tiempo estimado     : {total_est / 60:.0f}–{total_est * 2 / 60:.0f} min (según hardware)")
    print(f"\n  Leyenda progreso    : M=MCTS gana  r=Random gana  ·=empate/límite\n")

    # ── Crear agentes una sola vez ─────────────────────────────────────
    # MCTSAgent.__init__ llama a call_load_file() que tiene sleep(2).
    # Se crean dos instancias (P1 y P2) para poder alternar lados sin
    # recrear el objeto entre secciones.
    print("  Creando agentes MCTS (≈4s por el sleep de call_load_file)...")
    t0      = time.time()
    mcts_p1 = MCTSAgent(1, name="MCTS")
    mcts_p2 = MCTSAgent(2, name="MCTS")
    rand_p1 = RandomAgent(1, name="Random")
    rand_p2 = RandomAgent(2, name="Random")
    print(f"  Agentes listos en {time.time() - t0:.1f}s\n")

    all_results = []

    # ══════════════════════════════════════════════════════════════════
    # SECCIÓN 1 — Random vs Random (sanity check)
    #
    # Verifica que el motor del juego no favorezca artificialmente al
    # Player 1 ni al Player 2. Si el resultado es muy desbalanceado,
    # el juego estaría sesgado y el benchmark no sería válido.
    # ══════════════════════════════════════════════════════════════════
    print("─" * 60)
    print("  SECCIÓN 1 — Random vs Random  (sanity check de balance)")
    print("─" * 60)

    r_rvr = run_experiment(
        "Random(P1) vs Random(P2)",
        rand_p1, rand_p2,
        N_RANDOM_VS_RANDOM,
        mcts_player=None,
    )
    all_results.append(r_rvr)

    # ══════════════════════════════════════════════════════════════════
    # SECCIÓN 2 — MCTS vs Random (rendimiento principal)
    #
    # Se prueba MCTS en ambos lados para aislar el sesgo de turno
    # (el Player 1 puede tener ligera ventaja por ir primero).
    # El resultado combinado da una estimación más robusta del WR.
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 60)
    print(f"  SECCIÓN 2 — MCTS vs Random  (TIME_LIMIT = 0.2s)")
    print("─" * 60)

    mcts_p1.time_limit = 0.2
    r_s2_p1 = run_experiment(
        "MCTS(P1) vs Random(P2)  [TL=0.20s]",
        mcts_p1, rand_p2,
        N_MCTS_VS_RANDOM,
        mcts_player=1,
    )

    mcts_p2.time_limit = 0.2
    r_s2_p2 = run_experiment(
        "Random(P1) vs MCTS(P2)  [TL=0.20s]",
        rand_p1, mcts_p2,
        N_MCTS_VS_RANDOM,
        mcts_player=2,
    )

    # Resultado combinado de la sección 2 (resumen para la tabla)
    r_s2_total = ExpResult.combine(
        "  ══ TOTAL sección 2",
        r_s2_p1, r_s2_p2,
    )
    all_results += [r_s2_p1, r_s2_p2, r_s2_total]

    # ══════════════════════════════════════════════════════════════════
    # SECCIÓN 3 — Efecto del tiempo de búsqueda
    #
    # Una propiedad fundamental de MCTS es que su calidad mejora con
    # más tiempo (más iteraciones = árbol más profundo y exacto).
    # Esta sección muestra empíricamente ese comportamiento.
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 60)
    print("  SECCIÓN 3 — Comparación por tiempo de búsqueda")
    print("─" * 60)

    for tl in TIME_LIMITS_TO_TEST:
        # Reusar los mismos objetos, solo cambiar el tiempo límite
        mcts_p1.time_limit = tl
        mcts_p2.time_limit = tl

        r_a = run_experiment(
            f"MCTS(P1) vs Random(P2)  [TL={tl:.2f}s]",
            mcts_p1, rand_p2,
            N_TIME_COMPARISON,
            mcts_player=1,
        )
        r_b = run_experiment(
            f"Random(P1) vs MCTS(P2)  [TL={tl:.2f}s]",
            rand_p1, mcts_p2,
            N_TIME_COMPARISON,
            mcts_player=2,
        )
        r_combo = ExpResult.combine(
            f"  ══ TOTAL TL={tl:.2f}s",
            r_a, r_b,
        )
        all_results += [r_a, r_b, r_combo]

    # ══════════════════════════════════════════════════════════════════
    # Tabla resumen final
    # ══════════════════════════════════════════════════════════════════
    total_elapsed = time.time() - t_benchmark_start
    print_table(all_results, total_elapsed)


if __name__ == "__main__":
    main()
