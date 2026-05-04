def call_load_file():
    """
    Función placeholder para mantener compatibilidad con los agentes base.
    Si luego se desea cargar un modelo, tabla o checkpoint, se implementa aquí.
    """
    return None


def get_opponent(player):
    return 2 if player == 1 else 1


def safe_legal_moves(state, player):
    return list(state.legal_moves(player))