# Plan de trabajo - Proyecto Final IA Morris

## Objetivo técnico
Construir un agente inteligente para Nine Men's Morris usando MCTS, PUCT, self-play y, si es viable, una red neuronal o función de evaluación aprendida.

## Carpeta de desarrollo
morris_dev

## Carpeta de competencia
morris_competition

## Estrategia
Primero se desarrollará el agente en morris_dev/agents/mcts_agent.py.
Cuando esté estable, se adaptará a la carpeta correspondiente del grupo dentro de morris_competition/agents/GRPX.

## Fases

### Fase 1: Análisis de la plataforma
- Entender GameState.
- Entender legal_moves.
- Entender apply_move.
- Entender apply_capture.
- Entender winner e is_terminal.
- Confirmar cómo el agente debe devolver movimientos.

### Fase 2: MCTS básico
- Crear nodos del árbol.
- Selección.
- Expansión.
- Simulación.
- Retropropagación.
- Elección del movimiento más visitado.

### Fase 3: Heurística
- Valorar formación de molinos.
- Bloquear molinos enemigos.
- Priorizar capturas.
- Valorar movilidad.
- Valorar cantidad de fichas propias y enemigas.

### Fase 4: PUCT
- Integrar una fórmula estilo AlphaZero.
- Usar una prioridad para guiar la búsqueda.

### Fase 5: Self-play
- Permitir que el agente juegue contra sí mismo.
- Guardar resultados.
- Usar esos resultados para ajustar decisiones.

### Fase 6: Adaptación a competencia
- Copiar el agente final a GRPX.
- Verificar imports.
- Probar contra otros grupos o agentes base.

### Fase 7: Presentación técnica
- Explicar funcionamiento.
- Mostrar resultados.
- Explicar decisiones de diseño.
- Preparar defensa oral.