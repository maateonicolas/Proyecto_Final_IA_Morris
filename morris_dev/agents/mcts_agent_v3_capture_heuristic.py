# agents/mcts_agent.py
#
# V3: MCTS básico (idéntico a V1) + choose_capture con heurística directa.
#
# Cambios respecto a V1 (mcts_agent_v1_mcts_basico.py):
#   1. from game_engine import MILLS, NEIGHBORS  (necesario para _score_capture)
#   2. Nueva función auxiliar _score_capture(state, pos)
#   3. choose_capture usa max(_score_capture) en vez de _run_mcts
#
# TODO completamente sin cambios: MCTSNode, _apply_move, choose_move,
# _run_mcts, _select, _simulate, _backpropagate, wins/visits.

import random
import math
import time
from .utils import call_load_file
from game_engine import MILLS, NEIGHBORS   # constantes del tablero, para _score_capture


# -----------------------------------------------------------------------
# Función auxiliar para rankear capturas (nueva en V3)
# -----------------------------------------------------------------------

def _score_capture(state, pos):
    """
    Puntúa la pieza rival en pos como candidato de captura. Mayor = mejor.

    Criterio 1 — Pieza no en molino:
      Ya garantizado por legal_captures() del motor del juego.
      legal_moves() cuando need_capture=True solo incluye piezas
      en molino si TODAS las del rival están en molino.
      Por eso no hay que filtrar aquí.

    Criterio 2 — Amenaza de molino activa (+4 por línea):
      Una línea es una "amenaza" cuando tiene 2 piezas del rival + 1 vacío.
      Capturar pos si participa en esa línea destruye la amenaza
      antes de que el rival pueda completar el molino.

    Criterio 3 — Conectividad con otras fichas rivales (+1 por vecino):
      Una pieza con más vecinos del rival está más integrada en su red
      y es tácticamente más influyente. Capturarla aísla esas conexiones.
    """
    opp   = 3 - state.cur   # dueño de la pieza que vamos a capturar
    board = state.board
    score = 0

    # Criterio 2: amenazas activas en las que pos participa
    for a, b, c in MILLS:
        if pos not in (a, b, c):
            continue
        vals = (board[a], board[b], board[c])
        if vals.count(opp) == 2 and vals.count(0) == 1:
            score += 4   # destruir esta amenaza vale bastante

    # Criterio 3: vecinos del rival (conectividad)
    score += sum(1 for n in NEIGHBORS[pos] if board[n] == opp)

    return score


# -----------------------------------------------------------------------
# Nodo del árbol MCTS — idéntico a V1
# -----------------------------------------------------------------------

class MCTSNode:
    """
    Nodo del árbol de búsqueda MCTS.

    Cada nodo guarda:
      - state       : estado del juego al llegar aquí
      - parent      : nodo padre (None en la raíz)
      - move        : movimiento que generó este nodo desde el padre
      - children    : lista de nodos hijo ya expandidos
      - visits      : cuántas simulaciones pasaron por este nodo
      - wins        : victorias acumuladas del agente en esas simulaciones
      - untried_moves: movimientos legales todavía no expandidos
    """

    __slots__ = ('state', 'parent', 'move', 'children',
                 'visits', 'wins', 'untried_moves')

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        # Movimientos legales del jugador que tiene el turno en este nodo
        self.untried_moves = list(state.legal_moves(state.cur))

    # ------------------------------------------------------------------
    # UCB1: balance entre exploración y explotación
    # ------------------------------------------------------------------

    def ucb1(self, parent_player, agent_number, c=1.414):
        """
        Fórmula UCB1.
        - Si el padre es el agente: maximizar win_rate (buscamos lo mejor para nosotros).
        - Si el padre es el oponente: invertir perspectiva (el oponente elegirá
          el movimiento que más nos perjudique, así que buscamos el menor win_rate
          desde su punto de vista).
        El parámetro c controla el peso de la exploración (√2 por defecto).
        """
        if self.visits == 0:
            return float('inf')

        win_rate = self.wins / self.visits
        if parent_player != agent_number:
            win_rate = 1.0 - win_rate   # perspectiva del oponente → invertir

        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return win_rate + exploration

    def best_child(self, agent_number, c=1.414):
        """Retorna el hijo con mayor UCB1 desde la perspectiva del jugador actual."""
        cur = self.state.cur
        return max(self.children,
                   key=lambda child: child.ucb1(cur, agent_number, c))

    # ------------------------------------------------------------------
    # Expansión: agrega un nodo hijo nuevo
    # ------------------------------------------------------------------

    def expand(self):
        """
        Saca un movimiento de untried_moves, lo aplica en una copia del estado
        y crea un nodo hijo. Retorna ese hijo.
        """
        move = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        new_state = self.state.copy()
        _apply_move(new_state, move)
        child = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child)
        return child


# -----------------------------------------------------------------------
# Función auxiliar: aplica cualquier tipo de movimiento al estado
# (idéntica a V1)
# -----------------------------------------------------------------------

def _apply_move(state, move):
    """
    Aplica al estado un movimiento de cualquier tipo:
      - "capture": llama a apply_capture(pos)
      - "place" / "move": llama a apply_move(move)
    """
    if move[0] == "capture":
        state.apply_capture(move[2])
    else:
        state.apply_move(move)


# -----------------------------------------------------------------------
# Agente MCTS V3
# -----------------------------------------------------------------------

class MCTSAgent:
    def __init__(self, agent_num, name="MCTSBot"):
        self.name = name
        self.number_of_wins = 0
        self.agent_number = agent_num
        self.time_limit = 1.0   # segundos máximos de búsqueda por movimiento
        self.tree = call_load_file()

    # ------------------------------------------------------------------
    # Interfaz obligatoria
    # ------------------------------------------------------------------

    def choose_move(self, state, move_choice_dict):
        """
        Interfaz requerida por el motor del juego.
        Ejecuta MCTS y guarda el mejor movimiento en move_choice_dict["move_choice"].
        Si ocurre cualquier error, cae a un movimiento aleatorio legal (fallback).
        [Idéntico a V1]
        """
        try:
            moves = state.legal_moves(self.agent_number)
            if not moves:
                return                          # sin movimientos posibles
            if len(moves) == 1:
                move_choice_dict["move_choice"] = moves[0]
                return                          # solo una opción, no hace falta buscar
            move_choice_dict["move_choice"] = self._run_mcts(state)
        except Exception:
            # Fallback: nunca dejar move_choice_dict vacío
            moves = state.legal_moves(self.agent_number)
            if moves:
                move_choice_dict["move_choice"] = random.choice(moves)

    def choose_capture(self, state, capture_choice_dict):
        """
        V3: heurística directa para elegir la captura (no MCTS).

        Con típicamente 1–5 opciones de captura, rankear por _score_capture
        es más rápido y confiable que correr MCTS sobre esas pocas opciones.
        El árbol MCTS queda libre para enfocarse en choose_move.

        Orden de prioridad implementado:
          1. Piezas no en molino → ya filtradas por legal_captures() del motor.
          2. Piezas en amenaza activa del rival → +4 puntos en _score_capture.
          3. Piezas con mayor conectividad → +1/vecino en _score_capture.
          4. Fallback aleatorio si cualquier error interrumpe la evaluación.
        """
        try:
            moves = state.legal_moves(self.agent_number)
            if not moves:
                return
            if len(moves) == 1:
                capture_choice_dict["capture_choice"] = moves[0][2]
                return
            # Elegir la pieza con mayor puntuación heurística
            best = max(moves, key=lambda m: _score_capture(state, m[2]))
            capture_choice_dict["capture_choice"] = best[2]
        except Exception:
            moves = state.legal_moves(self.agent_number)
            if moves:
                capture_choice_dict["capture_choice"] = random.choice(moves)[2]

    # ------------------------------------------------------------------
    # Fase 0: bucle principal MCTS — idéntico a V1
    # ------------------------------------------------------------------

    def _run_mcts(self, state):
        """
        Bucle principal MCTS. Itera selección→expansión→simulación→retropropagación
        durante self.time_limit segundos y retorna el movimiento del hijo más visitado.
        """
        root = MCTSNode(state)
        deadline = time.time() + self.time_limit

        while time.time() < deadline:
            # --- Fase 1: Selección ---
            node = self._select(root)

            # --- Fase 2: Expansión ---
            # Solo expandir si el nodo no es terminal y tiene movimientos pendientes
            if not node.state.is_terminal() and node.untried_moves:
                node = node.expand()

            # --- Fase 3: Simulación (rollout aleatorio) ---
            winner = self._simulate(node.state)

            # --- Fase 4: Retropropagación ---
            self._backpropagate(node, winner)

        # Selección final: el hijo de la raíz más visitado (explotación pura)
        if not root.children:
            # Ninguna iteración completó la expansión (tiempo muy corto)
            fallback = root.untried_moves if root.untried_moves else state.legal_moves(self.agent_number)
            return random.choice(fallback) if fallback else None

        best = max(root.children, key=lambda c: c.visits)
        return best.move

    # ------------------------------------------------------------------
    # Fase 1: Selección (UCB1 tree policy) — idéntica a V1
    # ------------------------------------------------------------------

    def _select(self, node):
        """
        Desciende el árbol eligiendo el hijo con mayor UCB1 en cada nivel
        hasta encontrar un nodo con movimientos sin expandir o un estado terminal.
        """
        while not node.state.is_terminal():
            if node.untried_moves:
                # Nodo parcialmente expandido → este es el candidato a expandir
                return node
            if not node.children:
                # Nodo sin hijos ni movimientos pendientes (no debería ocurrir si no es terminal)
                return node
            # Nodo totalmente expandido → bajar por UCB1
            node = node.best_child(self.agent_number)
        return node  # estado terminal

    # ------------------------------------------------------------------
    # Fase 3: Simulación / Rollout — idéntica a V1
    # ------------------------------------------------------------------

    def _simulate(self, state):
        """
        Realiza un rollout aleatorio desde el estado dado hasta un estado terminal.
        Maneja correctamente:
          - movimientos normales (place / move) con apply_move
          - capturas obligatorias (need_capture=True) con apply_capture
          - estados terminales con is_terminal()
        Retorna el ganador (1, 2) o None si no hay ganador tras el límite de profundidad.
        """
        sim = state.copy()
        max_depth = 150     # tope para evitar partidas infinitas en el rollout

        for _ in range(max_depth):
            if sim.is_terminal():
                break

            moves = sim.legal_moves(sim.cur)
            if not moves:
                break

            move = random.choice(moves)

            # legal_moves ya devuelve capturas cuando need_capture es True
            if move[0] == "capture":
                sim.apply_capture(move[2])
            else:
                sim.apply_move(move)

        return sim.winner()

    # ------------------------------------------------------------------
    # Fase 4: Retropropagación — idéntica a V1
    # ------------------------------------------------------------------

    def _backpropagate(self, node, winner):
        """
        Recorre el árbol desde el nodo hoja hasta la raíz sumando:
          +1.0  si ganó el agente
          +0.5  si fue empate (winner == None)
          +0.0  si ganó el oponente
        Incrementa el contador de visitas en cada nodo del camino.
        """
        while node is not None:
            node.visits += 1
            if winner == self.agent_number:
                node.wins += 1.0
            elif winner is None:
                node.wins += 0.5    # empate
            # derrota del agente: sumar 0 (no hace falta else)
            node = node.parent
