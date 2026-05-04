# Proyecto Final IA - Nine Men's Morris

## Descripción

Este proyecto implementa un agente inteligente para el juego **Nine Men's Morris** usando **Monte Carlo Tree Search (MCTS)** como motor principal de toma de decisiones.

El agente final integrado en la plataforma de competencia es `GRP1`. La versión actual utiliza MCTS básico con selección, expansión, simulación aleatoria y retropropagación. Durante el desarrollo se evaluaron versiones con heurísticas adicionales, pero se seleccionó la versión MCTS básica por estabilidad y desempeño comparativo.

---

## Participantes

| Nombre | Responsabilidad principal |
|---|---|
| Mateo Díaz | Integración del agente, pruebas, documentación técnica |
| Wilmer Cárdenas | Desarrollo del agente, benchmarks, análisis experimental |

---

## Arquitectura del proyecto

```text
Proyecto_Final_IA_Morris/
├── agents/
│   └── GRP1/
│       ├── grp1_agent.py
│       ├── mcts_puct.py
│       ├── model.py
│       └── utils.py
│
├── morris_competition/
│   ├── agents/
│   │   ├── GRP1/
│   │   │   ├── grp1_agent.py
│   │   │   ├── mcts_puct.py
│   │   │   ├── model.py
│   │   │   └── utils.py
│   │   ├── GRP2/
│   │   ├── GRP3/
│   │   └── ...
│   ├── game_engine.py
│   ├── load_agents.py
│   ├── pygame_ui.py
│   ├── benchmark_grp1_final.py
│   └── tests/
│
├── morris_dev/
│   ├── benchmark_agents.py
│   ├── benchmark_agents_v1.py
│   ├── benchmark_v1_vs_v2.py
│   ├── benchmark_v1_vs_v3.py
│   └── test_mcts_vs_random.py
│
├── training/
│   ├── self_play.py
│   ├── train.py
│   └── evaluate.py
│
├── docs/
│   ├── resultados_pruebas.md
│   └── checklist_defensa.md
│
├── ethics/
├── requirements.txt
└── README.md
```

---

## Componentes principales

### `morris_competition/`

Contiene la plataforma principal de competencia:

- Motor del juego.
- Interfaz gráfica en Pygame.
- Carga automática de agentes.
- Agentes por grupo.
- Benchmark final del agente `GRP1`.

Archivos importantes:

| Archivo | Descripción |
|---|---|
| `game_engine.py` | Implementa el estado del juego, reglas, movimientos legales, capturas, detección de terminalidad y ganador. |
| `load_agents.py` | Carga los agentes por grupo según el modo de competencia. |
| `pygame_ui.py` | Interfaz gráfica para visualizar partidas en tiempo real. |
| `benchmark_grp1_final.py` | Benchmark final del agente `GRP1` contra `GRP2` Random. |

---

### `morris_competition/agents/GRP1/`

Contiene el agente final del grupo.

| Archivo | Descripción |
|---|---|
| `grp1_agent.py` | Adaptador del agente para la plataforma. Implementa `choose_move()` y `choose_capture()`. |
| `mcts_puct.py` | Implementación actual del algoritmo MCTS básico. |
| `utils.py` | Funciones auxiliares usadas por el agente. |
| `model.py` | Esqueleto preparado para una futura red neuronal de política/valor. |

---

### `morris_dev/`

Contiene versiones y benchmarks usados durante el desarrollo experimental.

Estos archivos no son el agente final de competencia, pero sirven como evidencia de comparación entre versiones:

| Archivo | Descripción |
|---|---|
| `benchmark_agents.py` | Benchmark completo MCTS vs Random. |
| `benchmark_agents_v1.py` | Benchmark de la versión MCTS básica. |
| `benchmark_v1_vs_v2.py` | Comparación entre MCTS básico y MCTS con heurística completa. |
| `benchmark_v1_vs_v3.py` | Comparación entre MCTS básico y MCTS con heurística de captura. |
| `test_mcts_vs_random.py` | Prueba automática MCTS vs Random. |

---

### `training/`

Contiene archivos preparados para una futura extensión estilo AlphaZero.

| Archivo | Propósito |
|---|---|
| `self_play.py` | Generación futura de partidas del agente contra sí mismo. |
| `train.py` | Entrenamiento futuro de la red neuronal de política/valor. |
| `evaluate.py` | Evaluación futura de modelos entrenados. |

Actualmente estos archivos forman parte de la arquitectura propuesta, pero la versión final entregada se basa en MCTS básico.

---

## Funcionamiento del agente

El agente `GRP1` sigue el flujo de la plataforma:

1. La plataforma llama a `choose_move(state, move_choice_dict)`.
2. El agente obtiene los movimientos legales del estado.
3. MCTS ejecuta simulaciones durante un límite de tiempo.
4. Se selecciona el movimiento con mejor estadística.
5. El movimiento se guarda en `move_choice_dict["move_choice"]`.
6. Si se forma un molino, la plataforma llama a `choose_capture(state, capture_choice_dict)`.
7. El agente selecciona una captura legal y la guarda en `capture_choice_dict["capture_choice"]`.

---

## Algoritmo usado: Monte Carlo Tree Search

La versión actual implementa MCTS básico con las cuatro etapas clásicas:

### 1. Selección

Se recorre el árbol usando UCB1 para balancear:

- Explotación: elegir movimientos que han dado buenos resultados.
- Exploración: probar movimientos que todavía tienen pocas simulaciones.

### 2. Expansión

Cuando se encuentra un nodo con movimientos no explorados, se agrega un nuevo hijo al árbol.

### 3. Simulación

Desde el nuevo nodo se ejecuta una partida simulada usando movimientos aleatorios.

### 4. Retropropagación

El resultado de la simulación se propaga hacia atrás actualizando visitas y valores de los nodos.

---

## Versiones evaluadas durante el desarrollo

| Versión | Descripción | Resultado general |
|---|---|---|
| V1 | MCTS básico con rollouts aleatorios | Versión más estable |
| V2 | MCTS con heurística completa | No superó consistentemente a V1 |
| V3 | MCTS con heurística de captura | Rendimiento similar a V1 |

La versión final seleccionada fue **V1 MCTS básico**, por estabilidad y mejor desempeño comparativo.

---

## Resultados esperados de benchmark

El benchmark final se ejecuta con:

```bash
cd morris_competition
python benchmark_grp1_final.py
```

Este benchmark compara:

- `GRP1` como jugador 1 contra `GRP2` Random.
- `GRP1` como jugador 2 contra `GRP2` Random.
- Resultados combinados para reducir sesgo de turno.

Los resultados finales deben documentarse en:

```text
docs/resultados_pruebas.md
```

---

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv .venv
```

### 2. Activar entorno virtual

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Dependencias

El proyecto usa:

```text
pygame==2.6.1
pytest==9.0.3
numpy==2.4.4
tqdm==4.67.3
```

Se recomienda usar **Python 3.11.9** para evitar problemas de compatibilidad con Pygame.

---

## Ejecución de pruebas

Desde la carpeta `morris_competition`:

```bash
pytest tests
```

Resultado esperado:

```text
4 passed
```

---

## Ejecución de la interfaz gráfica

Desde la carpeta `morris_competition`:

```bash
python pygame_ui.py
```

La interfaz permite visualizar partidas en tiempo real entre agentes.

---

## Ejecución del benchmark final

Desde la carpeta `morris_competition`:

```bash
python benchmark_grp1_final.py
```

El benchmark imprime:

- Victorias de `GRP1`.
- Victorias de `GRP2`.
- Empates.
- Win rate de `GRP1`.
- Tiempo total de ejecución.

---

## Futuras mejoras

La arquitectura del proyecto deja preparado el camino para una versión estilo AlphaZero. Las mejoras futuras incluyen:

1. Implementar PUCT en lugar de UCB1.
2. Incorporar una red neuronal de política/valor.
3. Generar datos mediante self-play.
4. Entrenar iterativamente el modelo.
5. Comparar el agente entrenado contra el MCTS básico.
6. Evaluar rendimiento por número de simulaciones y tiempo por jugada.

---

## Estado actual

- [x] Plataforma ejecuta con Pygame.
- [x] `GRP1` se carga desde `load_agents.py`.
- [x] `GRP1` implementa `choose_move`.
- [x] `GRP1` implementa `choose_capture`.
- [x] `GRP1` devuelve movimientos legales.
- [x] Tests básicos pasan con `pytest`.
- [x] Benchmark final creado.
- [ ] Resultados finales documentados en `docs/resultados_pruebas.md`.

---

## Conclusión

El proyecto implementa un agente funcional para Nine Men's Morris basado en MCTS. La arquitectura separa la plataforma de competencia, el agente final, los benchmarks, la documentación y los módulos preparados para entrenamiento futuro.

La versión final actual prioriza estabilidad, compatibilidad con la plataforma y evaluación experimental frente a un agente aleatorio.
