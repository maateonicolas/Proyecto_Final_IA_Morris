ACTION_SIZE = 624


def get_opponent(player):
    return 2 if player == 1 else 1


def encode_state(state, player):
    """
    Codifica el estado desde el punto de vista del agente.

    Tamaño final: 80

    Estructura:
    - 24 posiciones propias
    - 24 posiciones rivales
    - 24 posiciones vacías
    - piezas propias en mano
    - piezas rivales en mano
    - piezas propias en tablero
    - piezas rivales en tablero
    - fase placing
    - fase moving
    - turno del agente
    - need_capture
    """

    opponent = get_opponent(player)

    own_positions = []
    opp_positions = []
    empty_positions = []

    for cell in state.board:
        own_positions.append(1.0 if cell == player else 0.0)
        opp_positions.append(1.0 if cell == opponent else 0.0)
        empty_positions.append(1.0 if cell == 0 else 0.0)

    features = []
    features.extend(own_positions)
    features.extend(opp_positions)
    features.extend(empty_positions)

    features.append(state.in_hand[player] / 9.0)
    features.append(state.in_hand[opponent] / 9.0)

    features.append(state.on_board[player] / 9.0)
    features.append(state.on_board[opponent] / 9.0)

    features.append(1.0 if state.phase == "placing" else 0.0)
    features.append(1.0 if state.phase == "moving" else 0.0)

    features.append(1.0 if state.cur == player else 0.0)
    features.append(1.0 if state.need_capture else 0.0)

    if len(features) != 80:
        raise ValueError(f"Encoded state must have size 80, got {len(features)}")

    return features


def action_to_index(action):
    """
    Convierte una acción del motor a índice de red.

    Formatos:
    - ("place", None, dst)
    - ("move", src, dst)
    - ("capture", None, pos)

    Espacio:
    - place:   0 - 23
    - move:    24 - 599
    - capture: 600 - 623
    """

    kind, src, dst = action

    if kind == "place":
        return dst

    if kind == "move":
        return 24 + src * 24 + dst

    if kind == "capture":
        return 600 + dst

    raise ValueError(f"Unknown action type: {kind}")


def index_to_action(index):
    """
    Convierte índice de red a acción.

    Esta función sirve para depuración.
    En juego real conviene filtrar usando legal_moves.
    """

    if 0 <= index < 24:
        return ("place", None, index)

    if 24 <= index < 600:
        raw = index - 24
        src = raw // 24
        dst = raw % 24
        return ("move", src, dst)

    if 600 <= index < 624:
        pos = index - 600
        return ("capture", None, pos)

    raise ValueError(f"Invalid action index: {index}")


def legal_action_indices(state, player):
    """
    Devuelve los índices de las acciones legales del estado actual.
    """

    legal_moves = state.legal_moves(player)
    return [action_to_index(move) for move in legal_moves]


def policy_to_legal_action(policy_probs, state, player):
    """
    Elige la acción legal con mayor probabilidad según la red.
    """

    legal_moves = state.legal_moves(player)

    if not legal_moves:
        return None

    best_move = None
    best_prob = -1.0

    for move in legal_moves:
        idx = action_to_index(move)
        prob = float(policy_probs[idx])

        if prob > best_prob:
            best_prob = prob
            best_move = move

    return best_move