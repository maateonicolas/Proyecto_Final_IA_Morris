# benchmark_v1_vs_v3.py
#
# Comparación directa: MCTS V1 (base) vs MCTS V3 (choose_capture heurístico).
#
#   V1 = mcts_agent_v1_mcts_basico.py         → MCTS puro, todo aleatorio
#   V3 = mcts_agent_v3_capture_heuristic.py   → MCTS puro + choose_capture con
#                                                heurística de 3 criterios:
#                                                  1. no en molino (motor)
#                                                  2. pieza en amenaza rival (+4)
#                                                  3. conectividad (+1/vecino)
#
# Estructura del experimento:
#   Serie 1 — V1(P1) vs V3(P2) : 20 partidas
#   Serie 2 — V3(P1) vs V1(P2) : 20 partidas
#   Total   : 40 partidas
#
# Pregunta que responde: ¿mejora capturar con heurística frente a usar MCTS
# para las capturas? V1 usaba _run_mcts también para choose_capture; V3 lo
# reemplaza por _score_capture determinista.
#
# Resultados usados en el README y la presentación universitaria.
# Leyenda de progreso: 3=V3 gana  1=V1 gana  ·=empate/límite de turnos

import random
import time
import importlib

from game_engine import GameState


# ═══════════════════════════════════════════════════════════════════════
# Configuración
# ═══════════════════════════════════════════════════════════════════════

TIME_LIMIT       = 0.2    # segundos de búsqueda MCTS por turno (igual para ambos)
N_GAMES_PER_SIDE = 20     # partidas por serie (20 + 20 = 40 total)
MAX_TURNS        = 300    # límite de turnos/partida para evitar ciclos infinitos


# ═══════════════════════════════════════════════════════════════════════
# Carga dinámica de los dos agentes
#
# Ambos archivos definen la clase "MCTSAgent".
# Se usa importlib.import_module con el nombre de paquete completo para
# que Python resuelva las importaciones relativas internas de cada módulo
# (from .utils import call_load_file, from game_engine import ...).
# ═══════════════════════════════════════════════════════════════════════

_v1_mod = importlib.import_module("agents.mcts_agent_v1_mcts_basico")
_v3_mod = importlib.import_module("agents.mcts_agent_v3_capture_heuristic")

MCTSAgentV1 = _v1_mod.MCTSAgent   # V1: MCTS básico, choose_capture con MCTS
MCTSAgentV3 = _v3_mod.MCTSAgent   # V3: MCTS básico, choose_capture con heurística


# ═══════════════════════════════════════════════════════════════════════
# Motor de partida sin interfaz gráfica
# ═══════════════════════════════════════════════════════════════════════

def play_game(agent1, agent2, max_turns=MAX_TURNS):
    """
    Ejecuta una partida completa entre agent1 (Player 1) y agent2 (Player 2).

    Maneja correctamente:
      - phase "placing" : colocación de piezas (9 por jugador)
      - phase "moving"  : movimiento y vuelo (cuando quedan 3 piezas)
      - need_capture    : captura obligatoria tras formar un molino
      - is_terminal()   : detección de fin de partida
      - fallback aleatorio si un agente devuelve None en cualquier decisión

    Retorna:
      1    → Player 1 ganó
      2    → Player 2 ganó
      None → se alcanzó MAX_TURNS sin ganador (se cuenta como empate)
    """
    state  = GameState()
    agents = {1: agent1, 2: agent2}

    for _ in range(max_turns):

        if state.is_terminal():
            break

        cur = agents[state.cur]

        if state.need_capture:
            # El jugador que formó el molino captura una pieza rival.
            # Recibe una COPIA del estado para no modificarlo directamente.
            d = {"capture_choice": None}
            cur.choose_capture(state.copy(), d)
            cap = d["capture_choice"]
            if cap is None:                          # fallback de seguridad
                legal = state.legal_moves(state.cur)
                cap = random.choice(legal)[2] if legal else None
            if cap is not None:
                state.apply_capture(cap)
        else:
            # Movimiento normal: "place" en placing, "move"/"fly" en moving.
            d = {"move_choice": None}
            cur.choose_move(state.copy(), d)
            move = d["move_choice"]
            if move is None:                         # fallback de seguridad
                legal = state.legal_moves(state.cur)
                move = random.choice(legal) if legal else None
            if move is not None:
                # apply_move setea need_capture si se forma molino;
                # el siguiente turno del bucle lo procesará automáticamente.
                state.apply_move(move)

    return state.winner()


# ═══════════════════════════════════════════════════════════════════════
# Contenedor de resultados de una serie
# ═══════════════════════════════════════════════════════════════════════

class SeriesResult:
    """
    Almacena estadísticas de una serie de partidas V1 vs V3.

    v3_player_num: número de jugador (1 o 2) que corresponde a V3 en esta serie.
    """

    def __init__(self, name, v3_player_num):
        self.name      = name
        self.v3_player = v3_player_num
        self.n_games   = 0
        self.v1_wins   = 0
        self.v3_wins   = 0
        self.draws     = 0
        self.elapsed   = 0.0

    def record(self, winner):
        """Registra el resultado de una partida."""
        self.n_games += 1
        if winner == self.v3_player:
            self.v3_wins += 1
        elif winner is not None:
            self.v1_wins += 1
        else:
            self.draws += 1

    @property
    def v3_winrate(self):
        return 100.0 * self.v3_wins / self.n_games if self.n_games > 0 else 0.0

    @property
    def v1_winrate(self):
        return 100.0 * self.v1_wins / self.n_games if self.n_games > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════
# Función para correr una serie de partidas
# ═══════════════════════════════════════════════════════════════════════

def run_series(agent1, agent2, n_games, v3_player_num, series_name):
    """
    Corre n_games partidas con agent1=P1, agent2=P2.

    v3_player_num indica qué número de jugador es V3 en esta serie.

    Imprime progreso compacto (10 resultados por línea):
      3 = V3 (capture heurístico) gana
      1 = V1 (básico)             gana
      · = empate / límite de turnos

    Retorna un SeriesResult.
    """
    res     = SeriesResult(series_name, v3_player_num)
    symbols = []
    t_start = time.time()

    print(f"\n  {series_name}")
    print(f"  {'─' * 52}")

    for i in range(n_games):
        winner = play_game(agent1, agent2)
        res.record(winner)

        # Símbolo compacto para el progreso visual
        if winner == v3_player_num:
            sym = "3"   # V3 gana
        elif winner is not None:
            sym = "1"   # V1 gana
        else:
            sym = "·"   # empate / límite de turnos

        symbols.append(sym)

        # Imprimir fila cada 10 partidas o al finalizar la última
        if (i + 1) % 10 == 0 or (i + 1) == n_games:
            start = (i // 10) * 10
            chunk = symbols[start:]
            label = f"{start + 1:3d}–{i + 1:3d}"
            print(f"    [{label}]  {'  '.join(chunk)}")

    res.elapsed = time.time() - t_start
    print(f"  → V3:{res.v3_wins}  V1:{res.v1_wins}  D:{res.draws}"
          f"   WR-V3={res.v3_winrate:.1f}%  ({res.elapsed:.0f}s)")

    return res


# ═══════════════════════════════════════════════════════════════════════
# Tabla resumen final
# ═══════════════════════════════════════════════════════════════════════

def print_summary(r1, r2, total_elapsed):
    """Imprime tabla con resultados de ambas series y el total combinado."""

    total_games = r1.n_games + r2.n_games
    total_v3    = r1.v3_wins + r2.v3_wins
    total_v1    = r1.v1_wins + r2.v1_wins
    total_draws = r1.draws   + r2.draws
    v3_wr_total = 100.0 * total_v3 / total_games if total_games > 0 else 0.0
    v1_wr_total = 100.0 * total_v1 / total_games if total_games > 0 else 0.0

    C = 42   # ancho columna nombre
    print("\n")
    print("═" * 78)
    print(f"  {'TABLA RESUMEN — V1 (básico) vs V3 (capture heurístico)':^76}")
    print("═" * 78)
    hdr = (f"  {'Serie':<{C}}"
           f"  {'N':>4}  {'V3W':>4}  {'V1W':>4}  {'D':>3}"
           f"  {'WR-V3':>7}  {'WR-V1':>7}  {'t(s)':>5}")
    print(hdr)
    print("  " + "─" * 76)

    for r in (r1, r2):
        print(
            f"  {r.name:<{C}}"
            f"  {r.n_games:>4}  {r.v3_wins:>4}  {r.v1_wins:>4}  {r.draws:>3}"
            f"  {r.v3_winrate:>6.1f}%  {r.v1_winrate:>6.1f}%  {r.elapsed:>5.0f}"
        )

    print("  " + "─" * 76)
    print(
        f"  {'TOTAL (combinado)':<{C}}"
        f"  {total_games:>4}  {total_v3:>4}  {total_v1:>4}  {total_draws:>3}"
        f"  {v3_wr_total:>6.1f}%  {v1_wr_total:>6.1f}%  {total_elapsed:>5.0f}"
    )
    print("═" * 78)
    print(f"  Tiempo total : {total_elapsed:.0f}s  ({total_elapsed / 60:.1f} min)")
    print("═" * 78)

    # Conclusión automática para usar en presentación
    print()
    if v3_wr_total > 65:
        print("  Conclusión: V3 supera claramente a V1.")
        print("  El choose_capture heurístico mejora el rendimiento del MCTS.")
    elif v3_wr_total > 55:
        print("  Conclusión: V3 supera a V1 con ventaja moderada.")
        print("  Aumentar N_GAMES puede confirmar si la diferencia es robusta.")
    elif v3_wr_total >= 45:
        print("  Conclusión: rendimiento similar entre V1 y V3.")
        print("  La heurística de captura no aporta ventaja medible con esta muestra.")
    else:
        print("  Conclusión: V1 superó a V3 en esta muestra.")
        print("  Revisar _score_capture o los pesos de los criterios.")
    print()


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    t_total_start = time.time()

    print("═" * 62)
    print("  BENCHMARK V1 vs V3 — Nine Men's Morris")
    print("═" * 62)
    print(f"\n  V1 : mcts_agent_v1_mcts_basico           (MCTS puro)")
    print(f"  V3 : mcts_agent_v3_capture_heuristic     (MCTS + capture heurístico)")
    print(f"\n  Diferencia: en V3, choose_capture usa _score_capture")
    print(f"  (max por amenazas +4 y conectividad +1) en vez de _run_mcts.")
    print(f"\n  TIME_LIMIT       : {TIME_LIMIT}s por turno (igual para ambos)")
    print(f"  Partidas por lado: {N_GAMES_PER_SIDE}  (total {2 * N_GAMES_PER_SIDE})")
    print(f"  MAX_TURNS        : {MAX_TURNS} turnos/partida (anti-ciclo)")
    print(f"\n  Leyenda: 3=V3 gana  1=V1 gana  ·=empate/límite\n")

    # ── Crear los cuatro agentes ───────────────────────────────────────
    # Cada MCTSAgent.__init__ llama a call_load_file() con sleep(2).
    # Se necesitan 4 instancias (V1 y V3, cada uno como P1 y P2) → ~8s.
    print("  Creando agentes (~8s por call_load_file × 4 instancias)...")
    t0    = time.time()
    v1_p1 = MCTSAgentV1(1, name="V1-P1")
    v1_p2 = MCTSAgentV1(2, name="V1-P2")
    v3_p1 = MCTSAgentV3(1, name="V3-P1")
    v3_p2 = MCTSAgentV3(2, name="V3-P2")

    for agent in (v1_p1, v1_p2, v3_p1, v3_p2):
        agent.time_limit = TIME_LIMIT

    print(f"  Agentes listos en {time.time() - t0:.1f}s\n")

    print("─" * 62)

    # ── Serie 1: V1 como Player 1, V3 como Player 2 ───────────────────
    # Si P1 tiene alguna ventaja de turno, esta serie puede perjudicar a V3.
    # El resultado combinado con la Serie 2 elimina ese sesgo.
    r1 = run_series(
        agent1        = v1_p1,
        agent2        = v3_p2,
        n_games       = N_GAMES_PER_SIDE,
        v3_player_num = 2,
        series_name   = f"V1(P1) vs V3(P2)  [TL={TIME_LIMIT}s]",
    )

    print("─" * 62)

    # ── Serie 2: V3 como Player 1, V1 como Player 2 ───────────────────
    # Invertir lados permite cancelar el posible sesgo de primer turno.
    r2 = run_series(
        agent1        = v3_p1,
        agent2        = v1_p2,
        n_games       = N_GAMES_PER_SIDE,
        v3_player_num = 1,
        series_name   = f"V3(P1) vs V1(P2)  [TL={TIME_LIMIT}s]",
    )

    # ── Resumen ───────────────────────────────────────────────────────
    total_elapsed = time.time() - t_total_start
    print_summary(r1, r2, total_elapsed)


if __name__ == "__main__":
    main()
