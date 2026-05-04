# benchmark_v1_vs_v2.py
#
# Comparación directa: MCTS Etapa 1 vs MCTS Etapa 2.
#
#   V1 = mcts_agent_v1_mcts_basico.py   → rollout completamente aleatorio
#   V2 = mcts_agent_v2_heuristica.py    → rollout guiado + evaluación heurística
#
# Estructura del experimento:
#   Serie 1 — V1(P1) vs V2(P2) : 20 partidas
#   Serie 2 — V2(P1) vs V1(P2) : 20 partidas
#   Total   : 40 partidas
#
# Objetivo: medir cuánto mejora realmente la heurística frente al MCTS base.
# Resultados usados en el README y presentación universitaria.
#
# Leyenda de progreso: 2=V2 gana  1=V1 gana  ·=empate/límite de turnos

import random
import time
import importlib

from game_engine import GameState


# ═══════════════════════════════════════════════════════════════════════
# Configuración
# ═══════════════════════════════════════════════════════════════════════

TIME_LIMIT       = 0.2    # segundos de búsqueda MCTS por turno (igual para ambos)
N_GAMES_PER_SIDE = 20     # partidas por serie (20 como P1 + 20 como P2 = 40 total)
MAX_TURNS        = 300    # límite de turnos por partida para evitar ciclos infinitos


# ═══════════════════════════════════════════════════════════════════════
# Carga dinámica de los dos agentes
#
# Ambos archivos definen una clase llamada "MCTSAgent", por lo que no
# se pueden importar con "import" estándar sin conflicto de nombres.
#
# Se usa importlib.import_module con el nombre de paquete completo
# ("agents.mcts_agent_v1_...") para que Python respete las importaciones
# relativas internas de cada módulo (from .utils import call_load_file).
# Equivalente a importlib.util.spec_from_file_location con submodule_search
# configurado, pero más limpio para módulos que ya pertenecen a un paquete.
# ═══════════════════════════════════════════════════════════════════════

_v1_mod = importlib.import_module("agents.mcts_agent_v1_mcts_basico")
_v2_mod = importlib.import_module("agents.mcts_agent_v2_heuristica")

MCTSAgentV1 = _v1_mod.MCTSAgent   # Etapa 1: MCTS básico, rollout aleatorio
MCTSAgentV2 = _v2_mod.MCTSAgent   # Etapa 2: MCTS + heurística, rollout guiado


# ═══════════════════════════════════════════════════════════════════════
# Motor de partida sin interfaz gráfica
# (misma lógica que benchmark_agents.py, probada y verificada)
# ═══════════════════════════════════════════════════════════════════════

def play_game(agent1, agent2, max_turns=MAX_TURNS):
    """
    Ejecuta una partida completa entre agent1 (Player 1) y agent2 (Player 2).

    Maneja correctamente:
      - phase "placing" : colocación de piezas
      - phase "moving"  : movimiento y vuelo (3 piezas)
      - need_capture    : captura obligatoria tras formar molino
      - is_terminal()   : fin de partida
      - fallback aleatorio si un agente devuelve None

    Retorna:
      1    → Player 1 ganó
      2    → Player 2 ganó
      None → límite de turnos alcanzado (se cuenta como empate)
    """
    state  = GameState()
    agents = {1: agent1, 2: agent2}

    for _ in range(max_turns):

        if state.is_terminal():
            break

        cur = agents[state.cur]

        if state.need_capture:
            # El jugador que formó el molino debe capturar una pieza rival.
            # El agente recibe una COPIA del estado para no modificarlo directamente.
            d = {"capture_choice": None}
            cur.choose_capture(state.copy(), d)
            cap = d["capture_choice"]
            if cap is None:                              # fallback de seguridad
                legal = state.legal_moves(state.cur)
                cap = random.choice(legal)[2] if legal else None
            if cap is not None:
                state.apply_capture(cap)
        else:
            # Movimiento normal: "place" en placing, "move"/"fly" en moving.
            d = {"move_choice": None}
            cur.choose_move(state.copy(), d)
            move = d["move_choice"]
            if move is None:                             # fallback de seguridad
                legal = state.legal_moves(state.cur)
                move = random.choice(legal) if legal else None
            if move is not None:
                # apply_move setea need_capture en el estado si se forma molino;
                # el siguiente turno del bucle lo procesará automáticamente.
                state.apply_move(move)

    return state.winner()


# ═══════════════════════════════════════════════════════════════════════
# Contenedor de resultados de una serie
# ═══════════════════════════════════════════════════════════════════════

class SeriesResult:
    """
    Almacena estadísticas de una serie de partidas V1 vs V2.

    v2_player_num: número de jugador (1 o 2) que corresponde a V2 en esta serie.
    """

    def __init__(self, name, v2_player_num):
        self.name        = name
        self.v2_player   = v2_player_num
        self.n_games     = 0
        self.v1_wins     = 0
        self.v2_wins     = 0
        self.draws       = 0
        self.elapsed     = 0.0

    def record(self, winner):
        """Registra el resultado de una partida."""
        self.n_games += 1
        if winner == self.v2_player:
            self.v2_wins += 1
        elif winner is not None:
            self.v1_wins += 1
        else:
            self.draws += 1

    @property
    def v2_winrate(self):
        return 100.0 * self.v2_wins / self.n_games if self.n_games > 0 else 0.0

    @property
    def v1_winrate(self):
        return 100.0 * self.v1_wins / self.n_games if self.n_games > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════
# Función para correr una serie de partidas
# ═══════════════════════════════════════════════════════════════════════

def run_series(agent1, agent2, n_games, v2_player_num, series_name):
    """
    Corre n_games partidas con agent1=P1, agent2=P2.

    v2_player_num indica qué número de jugador es V2 en esta serie
    para llevar el conteo correcto de victorias.

    Imprime progreso compacto (10 resultados por línea):
      2 = V2 (heurística) gana
      1 = V1 (básico)     gana
      · = empate / límite de turnos

    Retorna un SeriesResult.
    """
    res     = SeriesResult(series_name, v2_player_num)
    symbols = []
    t_start = time.time()

    print(f"\n  {series_name}")
    print(f"  {'─' * 52}")

    for i in range(n_games):
        winner = play_game(agent1, agent2)
        res.record(winner)

        # Símbolo compacto para el progreso
        if winner == v2_player_num:
            sym = "2"   # V2 (heurística) gana
        elif winner is not None:
            sym = "1"   # V1 (básico) gana
        else:
            sym = "·"   # empate / límite

        symbols.append(sym)

        # Imprimir fila cada 10 partidas o al finalizar la última
        if (i + 1) % 10 == 0 or (i + 1) == n_games:
            start = (i // 10) * 10
            chunk = symbols[start:]
            label = f"{start + 1:3d}–{i + 1:3d}"
            print(f"    [{label}]  {'  '.join(chunk)}")

    res.elapsed = time.time() - t_start
    print(f"  → V2:{res.v2_wins}  V1:{res.v1_wins}  D:{res.draws}"
          f"   WR-V2={res.v2_winrate:.1f}%  ({res.elapsed:.0f}s)")

    return res


# ═══════════════════════════════════════════════════════════════════════
# Tabla resumen final
# ═══════════════════════════════════════════════════════════════════════

def print_summary(r1, r2, total_elapsed):
    """Imprime tabla con resultados de ambas series y el total combinado."""

    total_games = r1.n_games + r2.n_games
    total_v2    = r1.v2_wins + r2.v2_wins
    total_v1    = r1.v1_wins + r2.v1_wins
    total_draws = r1.draws   + r2.draws
    v2_wr_total = 100.0 * total_v2 / total_games if total_games > 0 else 0.0
    v1_wr_total = 100.0 * total_v1 / total_games if total_games > 0 else 0.0

    C = 40   # ancho columna nombre
    print("\n")
    print("═" * 75)
    print(f"  {'TABLA RESUMEN — V1 (básico) vs V2 (heurística)':^73}")
    print("═" * 75)
    hdr = (f"  {'Serie':<{C}}"
           f"  {'N':>4}  {'V2W':>4}  {'V1W':>4}  {'D':>3}"
           f"  {'WR-V2':>7}  {'WR-V1':>7}  {'t(s)':>5}")
    print(hdr)
    print("  " + "─" * 73)

    for r in (r1, r2):
        print(
            f"  {r.name:<{C}}"
            f"  {r.n_games:>4}  {r.v2_wins:>4}  {r.v1_wins:>4}  {r.draws:>3}"
            f"  {r.v2_winrate:>6.1f}%  {r.v1_winrate:>6.1f}%  {r.elapsed:>5.0f}"
        )

    print("  " + "─" * 73)
    v2_wr_str = f"{v2_wr_total:>6.1f}%"
    v1_wr_str = f"{v1_wr_total:>6.1f}%"
    print(
        f"  {'TOTAL (combinado)':<{C}}"
        f"  {total_games:>4}  {total_v2:>4}  {total_v1:>4}  {total_draws:>3}"
        f"  {v2_wr_str}  {v1_wr_str}  {total_elapsed:>5.0f}"
    )
    print("═" * 75)
    print(f"  Tiempo total : {total_elapsed:.0f}s  ({total_elapsed / 60:.1f} min)")
    print("═" * 75)

    # Conclusión automática para presentación
    print()
    if v2_wr_total > 65:
        print(f"  Conclusión: V2 (heurística) supera claramente a V1 (básico).")
        print(f"  La heurística mejora el rendimiento del MCTS de forma significativa.")
    elif v2_wr_total > 50:
        print(f"  Conclusión: V2 (heurística) supera a V1 (básico) con ventaja moderada.")
        print(f"  Incrementar TIME_LIMIT o N_GAMES puede confirmar la tendencia.")
    elif v2_wr_total > 40:
        print(f"  Conclusión: rendimiento similar entre V1 y V2.")
        print(f"  Con 40 partidas la diferencia puede no ser estadísticamente significativa.")
    else:
        print(f"  Conclusión: V1 (básico) superó a V2 en esta muestra.")
        print(f"  Revisar los pesos heurísticos o aumentar TIME_LIMIT.")
    print()


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    t_total_start = time.time()

    print("═" * 60)
    print("  BENCHMARK V1 vs V2 — Nine Men's Morris")
    print("═" * 60)
    print(f"\n  V1 : mcts_agent_v1_mcts_basico   (rollout aleatorio)")
    print(f"  V2 : mcts_agent_v2_heuristica    (rollout guiado + heurística)")
    print(f"\n  TIME_LIMIT       : {TIME_LIMIT}s por turno (igual para ambos)")
    print(f"  Partidas por lado: {N_GAMES_PER_SIDE}  (total {2 * N_GAMES_PER_SIDE})")
    print(f"  MAX_TURNS        : {MAX_TURNS} turnos/partida (anti-ciclo)")
    print(f"\n  Leyenda: 2=V2 gana  1=V1 gana  ·=empate/límite\n")

    # ── Crear los cuatro agentes necesarios ───────────────────────────
    # Cada MCTSAgent.__init__ llama a call_load_file() con sleep(2).
    # Se crean 4 instancias (V1 y V2, cada uno como P1 y P2) → ~8s de carga.
    print("  Creando agentes (~8s por call_load_file × 4 instancias)...")
    t0      = time.time()
    v1_p1   = MCTSAgentV1(1, name="V1-P1")
    v1_p2   = MCTSAgentV1(2, name="V1-P2")
    v2_p1   = MCTSAgentV2(1, name="V2-P1")
    v2_p2   = MCTSAgentV2(2, name="V2-P2")

    for agent in (v1_p1, v1_p2, v2_p1, v2_p2):
        agent.time_limit = TIME_LIMIT

    print(f"  Agentes listos en {time.time() - t0:.1f}s\n")

    print("─" * 60)

    # ── Serie 1: V1 como Player 1, V2 como Player 2 ──────────────────
    # Elimina el sesgo de turno: si P1 tiene ventaja por ir primero,
    # esta serie podría favorecerla a V1.
    r1 = run_series(
        agent1        = v1_p1,
        agent2        = v2_p2,
        n_games       = N_GAMES_PER_SIDE,
        v2_player_num = 2,
        series_name   = f"V1(P1) vs V2(P2)  [TL={TIME_LIMIT}s]",
    )

    print("─" * 60)

    # ── Serie 2: V2 como Player 1, V1 como Player 2 ──────────────────
    # Al invertir los lados, el resultado combinado elimina el sesgo de turno.
    r2 = run_series(
        agent1        = v2_p1,
        agent2        = v1_p2,
        n_games       = N_GAMES_PER_SIDE,
        v2_player_num = 1,
        series_name   = f"V2(P1) vs V1(P2)  [TL={TIME_LIMIT}s]",
    )

    # ── Resumen ───────────────────────────────────────────────────────
    total_elapsed = time.time() - t_total_start
    print_summary(r1, r2, total_elapsed)


if __name__ == "__main__":
    main()
