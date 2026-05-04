# agents/mcts_agent.py
#
# ═══════════════════════════════════════════════════════════════════════
# ETAPA 1 (base):  MCTS básico con rollout completamente aleatorio.
# ETAPA 2 (aquí): MCTS con función de evaluación heurística.
#
# Cambios respecto a Etapa 1:
#   1. Se importan MILLS y NEIGHBORS desde game_engine para calcular
#      amenazas y conectividad sin modificar el motor del juego.
#   2. Seis nuevas funciones heurísticas a nivel módulo:
#        _count_mills, _count_threats,
#        _move_forms_mill, _move_blocks_opponent_threat,
#        _rank_capture, _weighted_move
#   3. _simulate → rollout semi-guiado:
#        capturas priorizan piezas en amenazas activas del rival;
#        movimientos normales usan selección ponderada (molino×10, bloqueo×5).
#   4. _evaluate → nueva función heurística [0,1] para estados no terminales.
#   5. _backpropagate → acepta float directamente (antes convertía winner int).
#   6. choose_capture → fallback usa _rank_capture en vez de azar puro.
# ═══════════════════════════════════════════════════════════════════════

import random
import math
import time
from .utils import call_load_file
from game_engine import MILLS, NEIGHBORS    # constantes del tablero de Morris


# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES HEURÍSTICAS (nivel módulo)
# Estas funciones son puras: leen el estado pero no lo modifican.
# ═══════════════════════════════════════════════════════════════════════

def _count_mills(board, player):
    """Cuenta molinos completos del jugador en el tablero actual."""
    return sum(1 for a, b, c in MILLS
               if board[a] == board[b] == board[c] == player)


def _count_threats(board, player):
    """
    Cuenta amenazas de molino del jugador:
    líneas con exactamente 2 fichas del jugador y 1 casilla vacía.
    Una amenaza se puede convertir en molino en el próximo turno.
    """
    count = 0
    for a, b, c in MILLS:
        vals = (board[a], board[b], board[c])
        if vals.count(player) == 2 and vals.count(0) == 1:
            count += 1
    return count


def _move_forms_mill(state, move):
    """
    Verifica si el movimiento formaría un molino sin modificar el estado.

    Para movimientos de tipo "move" (desplazamiento), tiene en cuenta que
    la casilla de origen (src) quedará vacía y no puede completar un molino.
    """
    kind, src, dst = move
    if kind not in ("place", "move"):
        return False

    player = state.cur
    board  = state.board

    for a, b, c in MILLS:
        if dst not in (a, b, c):
            continue
        forms = True
        for pos in (a, b, c):
            if pos == dst:
                continue                     # dst será ocupado por el jugador
            if kind == "move" and pos == src:
                forms = False               # src quedará vacío tras el movimiento
                break
            if board[pos] != player:
                forms = False
                break
        if forms:
            return True
    return False


def _move_blocks_opponent_threat(state, move):
    """
    Verifica si el movimiento bloquea una amenaza de molino del oponente.

    Bloquear = colocar una ficha en la casilla vacía de una línea donde
    el rival ya tiene las otras dos piezas.
    """
    kind, src, dst = move
    if kind not in ("place", "move"):
        return False

    opp   = 3 - state.cur
    board = state.board

    for a, b, c in MILLS:
        if dst not in (a, b, c):
            continue
        others = [pos for pos in (a, b, c) if pos != dst]
        if all(board[pos] == opp for pos in others):
            return True
    return False


def _rank_capture(state, pos):
    """
    Puntúa qué tan valioso es capturar la pieza rival en la posición pos.
    Mayor puntuación = objetivo más prioritario.

    Criterios:
      a) Pieza en amenaza activa del rival (+4 por línea con 2 rivales + 1 vacío):
         capturarla destruye esa amenaza antes de que se complete el molino.
      b) Conectividad con otras fichas rivales (+1 por vecino rival):
         pieza más conectada = más versátil e influyente en el tablero.
    """
    opp   = 3 - state.cur   # dueño de la pieza que se va a capturar
    board = state.board
    score = 0

    for a, b, c in MILLS:
        if pos not in (a, b, c):
            continue
        vals = (board[a], board[b], board[c])
        # ¿Es pos parte de una amenaza activa del rival?
        if vals.count(opp) == 2 and vals.count(0) == 1:
            score += 4   # romper esta amenaza vale bastante

    # Vecinos ocupados por el rival = mayor conectividad = mayor peligro
    score += sum(1 for n in NEIGHBORS[pos] if board[n] == opp)
    return score


def _weighted_move(state, moves):
    """
    Selección ponderada de movimiento con pesos heurísticos:
      - Peso 10: el movimiento forma un molino  (máxima prioridad)
      - Peso  5: el movimiento bloquea una amenaza rival
      - Peso  1: movimiento neutro (comportamiento equivalente a aleatorio)

    Implementa muestreo de la distribución de pesos (similar a ruleta).
    Fallback a aleatorio si ocurre cualquier error en la evaluación.
    """
    try:
        weights = []
        for m in moves:
            if _move_forms_mill(state, m):
                weights.append(10)
            elif _move_blocks_opponent_threat(state, m):
                weights.append(5)
            else:
                weights.append(1)

        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0.0
        for m, w in zip(moves, weights):
            cumulative += w
            if r <= cumulative:
                return m
        return moves[-1]
    except Exception:
        return random.choice(moves)


# ═══════════════════════════════════════════════════════════════════════
# NODO DEL ÁRBOL MCTS (sin cambios respecto a Etapa 1)
# ═══════════════════════════════════════════════════════════════════════

class MCTSNode:
    """
    Nodo del árbol de búsqueda MCTS.

    Cada nodo almacena:
      state         : estado del juego al llegar aquí
      parent        : nodo padre (None en la raíz)
      move          : movimiento que generó este nodo desde el padre
      children      : hijos ya expandidos
      visits        : número de simulaciones que pasaron por este nodo
      wins          : suma de puntuaciones del agente en esas simulaciones
                      (cada puntuación es un float en [0, 1])
      untried_moves : movimientos legales todavía no expandidos
    """

    __slots__ = ('state', 'parent', 'move', 'children',
                 'visits', 'wins', 'untried_moves')

    def __init__(self, state, parent=None, move=None):
        self.state         = state
        self.parent        = parent
        self.move          = move
        self.children      = []
        self.visits        = 0
        self.wins          = 0.0
        self.untried_moves = list(state.legal_moves(state.cur))

    def ucb1(self, parent_player, agent_number, c=1.414):
        """
        Fórmula UCB1 con perspectiva alternada:
          - padre es el agente   → maximizar win_rate
          - padre es el oponente → invertir (oponente minimiza nuestro win_rate)
        El parámetro c = √2 ≈ 1.414 controla exploración vs explotación.
        """
        if self.visits == 0:
            return float('inf')
        win_rate = self.wins / self.visits
        if parent_player != agent_number:
            win_rate = 1.0 - win_rate
        return win_rate + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self, agent_number, c=1.414):
        """Retorna el hijo con mayor UCB1 desde la perspectiva del jugador actual."""
        cur = self.state.cur
        return max(self.children,
                   key=lambda child: child.ucb1(cur, agent_number, c))

    def expand(self):
        """Expande un movimiento no explorado y retorna el nuevo nodo hijo."""
        move      = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        new_state = self.state.copy()
        _apply_move(new_state, move)
        child = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child)
        return child


def _apply_move(state, move):
    """Aplica al estado un movimiento de cualquier tipo (place, move o capture)."""
    if move[0] == "capture":
        state.apply_capture(move[2])
    else:
        state.apply_move(move)


# ═══════════════════════════════════════════════════════════════════════
# AGENTE MCTS CON HEURÍSTICA (Etapa 2)
# ═══════════════════════════════════════════════════════════════════════

class MCTSAgent:
    def __init__(self, agent_num, name="MCTSBot"):
        self.name           = name
        self.number_of_wins = 0
        self.agent_number   = agent_num
        self.time_limit     = 1.0   # segundos de búsqueda por turno
        self.tree           = call_load_file()

    # ── Interfaz obligatoria ─────────────────────────────────────────

    def choose_move(self, state, move_choice_dict):
        """
        Elige el mejor movimiento con MCTS y lo guarda en move_choice_dict.
        Fallback aleatorio si cualquier error interrumpe el MCTS.
        """
        try:
            moves = state.legal_moves(self.agent_number)
            if not moves:
                return
            if len(moves) == 1:
                move_choice_dict["move_choice"] = moves[0]
                return
            move_choice_dict["move_choice"] = self._run_mcts(state)
        except Exception:
            moves = state.legal_moves(self.agent_number)
            if moves:
                move_choice_dict["move_choice"] = random.choice(moves)

    def choose_capture(self, state, capture_choice_dict):
        """
        Elige la mejor captura con MCTS y guarda la posición en capture_choice_dict.

        Fallback mejorado (Etapa 2): si MCTS falla, en vez de captura aleatoria
        usa _rank_capture para preferir la pieza rival más peligrosa.
        """
        try:
            moves = state.legal_moves(self.agent_number)
            if not moves:
                return
            if len(moves) == 1:
                capture_choice_dict["capture_choice"] = moves[0][2]
                return
            move = self._run_mcts(state)
            capture_choice_dict["capture_choice"] = move[2]
        except Exception:
            moves = state.legal_moves(self.agent_number)
            if moves:
                try:
                    # Fallback heurístico: capturar la pieza rival más peligrosa
                    best = max(moves, key=lambda m: _rank_capture(state, m[2]))
                    capture_choice_dict["capture_choice"] = best[2]
                except Exception:
                    capture_choice_dict["capture_choice"] = random.choice(moves)[2]

    # ── Bucle principal MCTS (sin cambios respecto a Etapa 1) ────────

    def _run_mcts(self, state):
        """
        Ejecuta el bucle MCTS durante self.time_limit segundos.
        Retorna el movimiento del hijo de la raíz más visitado.
        """
        root     = MCTSNode(state)
        deadline = time.time() + self.time_limit

        while time.time() < deadline:
            # Fase 1: Selección
            node = self._select(root)

            # Fase 2: Expansión
            if not node.state.is_terminal() and node.untried_moves:
                node = node.expand()

            # Fase 3: Simulación con rollout guiado (Etapa 2)
            score = self._simulate(node.state)

            # Fase 4: Retropropagación
            self._backpropagate(node, score)

        if not root.children:
            fallback = root.untried_moves or state.legal_moves(self.agent_number)
            return random.choice(fallback) if fallback else None

        # Selección final: hijo más visitado (explotación pura)
        return max(root.children, key=lambda c: c.visits).move

    # ── Fase 1: Selección (sin cambios) ─────────────────────────────

    def _select(self, node):
        """Baja por UCB1 hasta encontrar un nodo expandible o terminal."""
        while not node.state.is_terminal():
            if node.untried_moves:
                return node
            if not node.children:
                return node
            node = node.best_child(self.agent_number)
        return node

    # ── Fase 3: Simulación con rollout guiado (Etapa 2) ─────────────

    def _simulate(self, state):
        """
        Rollout semi-guiado desde state hasta terminal o max_depth.

        Política de rollout en cada paso:
          - Si es turno de captura (need_capture=True):
              con p=0.7 captura la pieza rival más peligrosa (_rank_capture),
              con p=0.3 captura aleatoria (mantiene exploración).
          - Si es movimiento normal:
              selección ponderada (_weighted_move):
                molino    × 10  →  máxima prioridad
                bloqueo   ×  5  →  prioridad media
                otros     ×  1  →  comportamiento aleatorio uniforme

        Resultado devuelto:
          Estado terminal real → 1.0 (victoria) / 0.5 (empate) / 0.0 (derrota)
          Estado no terminal   → _evaluate(state): estimación heurística en [0,1]
        """
        sim       = state.copy()
        max_depth = 150   # límite para evitar rollouts infinitos

        for _ in range(max_depth):
            if sim.is_terminal():
                break

            moves = sim.legal_moves(sim.cur)
            if not moves:
                break

            try:
                if moves[0][0] == "capture":
                    # Captura semi-guiada
                    if random.random() < 0.7:
                        move = max(moves, key=lambda m: _rank_capture(sim, m[2]))
                    else:
                        move = random.choice(moves)
                    sim.apply_capture(move[2])
                else:
                    # Movimiento normal ponderado
                    move = _weighted_move(sim, moves)
                    sim.apply_move(move)
            except Exception:
                # Fallback ante cualquier error en la política guiada
                move = random.choice(moves)
                if move[0] == "capture":
                    sim.apply_capture(move[2])
                else:
                    sim.apply_move(move)

        # Devolver resultado del rollout
        if sim.is_terminal():
            w = sim.winner()
            if w == self.agent_number:   return 1.0
            if w is None:                return 0.5
            return 0.0
        else:
            # Rollout cortado antes de terminar: usar evaluación heurística
            return self._evaluate(sim)

    # ── Evaluación heurística (Etapa 2) ─────────────────────────────

    def _evaluate(self, state):
        """
        Estimación heurística de la posición en [0, 1] desde la perspectiva
        del agente. 0 = derrota segura, 0.5 = posición neutral, 1 = victoria.

        Componentes y pesos (suman 1.0):
          - Diferencia de piezas   (0.30): más fichas propias en juego → mejor.
          - Molinos formados        (0.20): más molinos propios completos → mejor.
          - Amenazas de molino      (0.25): más líneas con 2 fichas + 1 vacío → mejor.
          - Movilidad               (0.15): más movimientos propios disponibles → mejor.
          - Base neutral            (0.10): ancla de 0.5 para evitar extremos.

        Cada componente usa suavizado de Laplace: (mío+1)/(mío+rival+2)
        → devuelve 0.5 exactamente cuando ambos jugadores son iguales.
        → nunca devuelve 0 ni 1 para estados no terminales.
        """
        me  = self.agent_number
        opp = 3 - me

        # Estados terminales tienen puntuación exacta, no heurística
        if state.is_terminal():
            w = state.winner()
            if w == me:   return 1.0
            if w is None: return 0.5
            return 0.0

        board = state.board

        # 1. Ventaja en número de piezas (on_board + in_hand = total restantes)
        my_total  = state.on_board[me]  + state.in_hand[me]
        opp_total = state.on_board[opp] + state.in_hand[opp]
        piece_adv = my_total / (my_total + opp_total) if (my_total + opp_total) > 0 else 0.5

        # 2. Ventaja en molinos completos
        my_mills  = _count_mills(board, me)
        opp_mills = _count_mills(board, opp)
        mill_adv  = (my_mills + 1) / (my_mills + opp_mills + 2)

        # 3. Ventaja en amenazas de molino (2 fichas del mismo color + 1 vacío)
        my_threats  = _count_threats(board, me)
        opp_threats = _count_threats(board, opp)
        threat_adv  = (my_threats + 1) / (my_threats + opp_threats + 2)

        # 4. Ventaja de movilidad (solo en fase moving; en placing ambos tienen igualdad)
        if state.phase == "moving":
            my_moves  = len(state.legal_moves(me))
            opp_moves = len(state.legal_moves(opp))
            mob_adv   = (my_moves + 1) / (my_moves + opp_moves + 2)
        else:
            mob_adv = 0.5   # neutral durante la fase de colocación

        # Puntuación final ponderada (todos los pesos suman 1.0)
        score = (piece_adv  * 0.30 +
                 mill_adv   * 0.20 +
                 threat_adv * 0.25 +
                 mob_adv    * 0.15 +
                 0.5        * 0.10)   # componente base: siempre neutral

        return max(0.0, min(1.0, score))

    # ── Fase 4: Retropropagación (actualizada en Etapa 2) ────────────

    def _backpropagate(self, node, score):
        """
        Propaga la puntuación (float en [0,1]) desde el nodo hoja hasta la raíz.

        En Etapa 1: score era 1.0/0.5/0.0 solo para estados terminales.
        En Etapa 2: score también puede ser un valor continuo dado por _evaluate
                    cuando el rollout termina antes de llegar a un estado terminal.

        La fórmula UCB1 (wins/visits) sigue siendo válida porque ambas cantidades
        son consistentes: wins acumula puntuaciones del mismo rango [0,1].
        """
        while node is not None:
            node.visits += 1
            node.wins   += score
            node = node.parent
