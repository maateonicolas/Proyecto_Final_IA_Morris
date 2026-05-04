# Proyecto Final IA — Nine Men's Morris

## 1. Descripción general

Este proyecto implementa agentes inteligentes para el juego **Nine Men's Morris** dentro de una plataforma de competencia basada en Python y Pygame.

El proyecto tiene dos líneas principales:

1. **Agente estable de competencia (`GRP1`)**  
   Versión final recomendada para competir. Usa **Monte Carlo Tree Search (MCTS)** con mejoras heurísticas.

2. **Pipeline AlphaZero-like experimental**  
   Implementa una arquitectura con **PUCT**, **red neuronal policy/value**, **self-play**, entrenamiento y evaluación de checkpoints.

La recomendación para competencia es mantener como agente principal la versión estable:

```text
GRP1 = MCTS básico + captura heurística + prioridad de molino inmediato
```

La red neuronal y el pipeline AlphaZero-like quedan como componente técnico experimental y como base para futuras mejoras.

---

## 2. Participantes

| Nombre | Responsabilidad principal |
|---|---|
| Mateo Díaz | Integración del agente, pruebas, benchmark, documentación técnica |
| Wilmer Cárdenas | Desarrollo del agente, evaluación experimental, soporte técnico |

---

## 3. Arquitectura del repositorio

```text
Proyecto_Final_IA_Morris/
├── README.md
├── requirements.txt
├── .gitignore
│
├── morris_competition/
│   ├── game_engine.py
│   ├── load_agents.py
│   ├── pygame_ui.py
│   ├── benchmark_grp1_final.py
│   │
│   ├── agents/
│   │   ├── GRP1/
│   │   │   ├── __init__.py
│   │   │   ├── grp1_agent.py
│   │   │   ├── mcts_puct.py
│   │   │   ├── model.py
│   │   │   ├── neural_utils.py
│   │   │   ├── neural_puct_mcts.py
│   │   │   ├── alphazero_agent.py
│   │   │   └── utils.py
│   │   │
│   │   ├── GRP2/
│   │   ├── GRP3/
│   │   └── ...
│   │
│   ├── training/
│   │   ├── __init__.py
│   │   ├── self_play.py
│   │   ├── train.py
│   │   ├── evaluate_model.py
│   │   ├── self_play_az.py
│   │   ├── train_az.py
│   │   ├── evaluate_az_model.py
│   │   ├── data/
│   │   │   ├── self_play_dataset.pkl
│   │   │   └── self_play_az_dataset.pkl
│   │   └── checkpoints/
│   │       ├── morris_net.pt
│   │       └── morris_net_az.pt
│   │
│   └── tests/
│       ├── test_load_agents.py
│       ├── test_grp1_choose_move.py
│       ├── test_grp1_choose_capture.py
│       ├── test_grp1_real_state.py
│       ├── test_neural_model.py
│       ├── test_neural_policy_action.py
│       ├── test_neural_puct_mcts.py
│       ├── test_alphazero_agent.py
│       ├── test_self_play.py
│       ├── test_self_play_az.py
│       ├── test_train.py
│       ├── test_train_az.py
│       ├── test_evaluate_model.py
│       └── test_evaluate_az_model.py
│
├── morris_dev/
│   ├── benchmark_agents.py
│   ├── benchmark_agents_v1.py
│   ├── benchmark_v1_vs_v2.py
│   ├── benchmark_v1_vs_v3.py
│   └── test_mcts_vs_random.py
│
├── docs/
│   ├── resultados_pruebas.md
│   └── checklist_defensa.md
│
└── ethics/
```

---

## 4. Directorios principales

### `morris_competition/`

Directorio principal del proyecto. Contiene:

- motor del juego,
- interfaz gráfica,
- carga de agentes,
- agente final `GRP1`,
- benchmarks,
- tests,
- entrenamiento y evaluación.

Este es el directorio que se debe usar para ejecutar la competencia.

---

### `morris_competition/agents/GRP1/`

Contiene el agente del grupo.

| Archivo | Estado | Descripción |
|---|---|---|
| `grp1_agent.py` | Estable | Agente oficial de competencia. Implementa `choose_move()` y `choose_capture()`. |
| `mcts_puct.py` | Estable | MCTS básico usado por el agente final. |
| `utils.py` | Estable | Funciones auxiliares. |
| `model.py` | Experimental | Red neuronal `MorrisNet` con policy head y value head. |
| `neural_utils.py` | Experimental | Codificación de estado y acciones. |
| `neural_puct_mcts.py` | Experimental | MCTS con PUCT guiado por red neuronal. |
| `alphazero_agent.py` | Experimental | Agente AlphaZero-like separado del agente estable. |

---

### `morris_competition/training/`

Contiene el pipeline de entrenamiento.

| Archivo | Descripción |
|---|---|
| `self_play.py` | Self-play inicial con política one-hot. |
| `train.py` | Entrenamiento inicial de `MorrisNet`. |
| `evaluate_model.py` | Evaluación del checkpoint inicial `morris_net.pt`. |
| `self_play_az.py` | Self-play AlphaZero-like con distribución de visitas PUCT. |
| `train_az.py` | Entrenamiento AlphaZero-like usando visit policy. |
| `evaluate_az_model.py` | Evaluación del checkpoint AlphaZero-like `morris_net_az.pt`. |

---

### `morris_dev/`

Carpeta de desarrollo histórico. Se conserva como evidencia de experimentación previa.

Incluye benchmarks para comparar:

- MCTS básico contra Random,
- V1 vs V2,
- V1 vs V3.

No es el directorio principal de competencia.

---

## 5. Agente final de competencia

El agente final recomendado para competir es:

```text
morris_competition/agents/GRP1/grp1_agent.py
```

Este agente usa:

1. **MCTS básico**
   - selección,
   - expansión,
   - simulación,
   - retropropagación.

2. **Captura heurística**
   - evalúa qué pieza rival conviene capturar,
   - prioriza amenazas de molino,
   - considera conectividad y movilidad rival.

3. **Prioridad de molino inmediato**
   - antes de ejecutar MCTS, revisa si existe un movimiento legal que forme molino inmediatamente,
   - si existe, lo toma directamente.

La plataforma llama al agente con esta interfaz:

```python
choose_move(state, move_choice_dict)
choose_capture(state, capture_choice_dict)
```

---

## 6. Resultado final del benchmark del agente estable

Benchmark ejecutado contra `GRP2 Random`:

```text
Partidas por lado: 10
MAX_TURNS        : 150
Total partidas   : 20
```

| Serie | Partidas | Victorias GRP1 | Victorias GRP2 | Empates | Win rate GRP1 |
|---|---:|---:|---:|---:|---:|
| GRP1(P1) vs GRP2(P2) | 10 | 10 | 0 | 0 | 100% |
| GRP2(P1) vs GRP1(P2) | 10 | 10 | 0 | 0 | 100% |
| Total | 20 | 20 | 0 | 0 | 100% |

Conclusión:

```text
GRP1 supera claramente al agente aleatorio y no registró derrotas ni empates en el benchmark medio final.
```

---

## 7. Red neuronal policy/value

Se implementó una primera red neuronal llamada `MorrisNet`.

### Entrada

La red recibe un vector de estado de tamaño `80`.

La codificación incluye:

- 24 posiciones propias,
- 24 posiciones rivales,
- 24 posiciones vacías,
- piezas propias en mano,
- piezas rivales en mano,
- piezas propias en tablero,
- piezas rivales en tablero,
- fase del juego,
- jugador actual,
- indicador de captura obligatoria.

### Salidas

| Salida | Tamaño | Descripción |
|---|---:|---|
| `policy_head` | 624 | Distribución sobre acciones posibles. |
| `value_head` | 1 | Valor del estado en rango `[-1, 1]`. |

### Espacio de acciones

```text
0 - 23       : place
24 - 599     : move/fly
600 - 623    : capture
```

---

## 8. Entrenamiento inicial de red neuronal

Primer entrenamiento con self-play simple:

| Métrica | Resultado |
|---|---:|
| Dataset | `self_play_dataset.pkl` |
| Ejemplos | 282 |
| Épocas | 15 |
| Batch size | 32 |
| Learning rate | 0.001 |
| Loss inicial | 7.4586 |
| Loss final | 3.9932 |
| Checkpoint | `training/checkpoints/morris_net.pt` |

Evaluación del checkpoint inicial:

| Métrica | Resultado |
|---|---|
| Acciones legales en estado inicial | 24 |
| Acción seleccionada | `('place', None, 6)` |
| Valor estimado | `-0.8146` |

---

## 9. Pipeline AlphaZero-like experimental

Además del agente estable, se implementó una arquitectura AlphaZero-like experimental.

Componentes:

1. `NeuralPUCTMCTS`
   - usa PUCT,
   - usa priors de la red neuronal,
   - devuelve distribución de visitas.

2. `AlphaZeroAgent`
   - agente experimental,
   - no reemplaza al `GRP1` estable.

3. `self_play_az.py`
   - genera partidas usando PUCT,
   - guarda `visit_policy` en lugar de one-hot policy.

4. `train_az.py`
   - entrena con distribución de visitas,
   - usa policy loss suave y value loss.

---

## 10. Resultados del self-play AlphaZero-like

Self-play AlphaZero-like ejecutado con:

```text
NUM_GAMES   : 10
MAX_TURNS   : 150
SIMULATIONS : 40
```

Resultado:

| Métrica | Resultado |
|---|---:|
| Partidas self-play AZ | 10 |
| Ejemplos generados | 1307 |
| Tipo de política | Distribución de visitas PUCT |
| Dataset | `training/data/self_play_az_dataset.pkl` |

Observación:

En esta primera versión, varias partidas alcanzaron el límite de turnos. Esto es esperable porque el agente AlphaZero-like aún está en fase experimental.

---

## 11. Entrenamiento AlphaZero-like

Entrenamiento ejecutado con `train_az.py`:

| Parámetro | Valor |
|---|---:|
| Dataset | `self_play_az_dataset.pkl` |
| Ejemplos | 1307 |
| Épocas | 30 |
| Batch size | 64 |
| Learning rate | 0.001 |
| Value loss weight | 1.0 |
| Loss inicial | 6.1569 |
| Loss final | 2.1281 |
| Policy loss final | 2.1130 |
| Value loss final | 0.0151 |
| Checkpoint | `training/checkpoints/morris_net_az.pt` |

Interpretación:

La pérdida total disminuyó de `6.1569` a `2.1281`, lo que indica que la red aprendió a aproximar la política de visitas generada por PUCT y el valor final de los estados del self-play.

---

## 12. Estado de tests

Último estado confirmado:

```text
13 passed
1 test pendiente de corregir relacionado con evaluate_az_model.py
```

El test pendiente se corrige verificando que el archivo:

```text
morris_competition/training/evaluate_az_model.py
```

defina correctamente:

```python
CHECKPOINT_PATH
load_az_checkpoint()
```

Después de corregirlo, el resultado esperado es:

```text
14 passed
```

---

## 13. Instalación

Se recomienda usar Python 3.11.9.

### Crear entorno virtual

```bash
python -m venv .venv
```

### Activar entorno virtual en Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 14. Dependencias

`requirements.txt` recomendado:

```text
pygame==2.6.1
pytest==9.0.3
numpy==2.4.4
tqdm==4.67.3
torch
```

---

## 15. Comandos principales

### Ejecutar tests

```bash
cd morris_competition
pytest tests
```

### Ejecutar interfaz gráfica

```bash
cd morris_competition
python pygame_ui.py
```

### Ejecutar benchmark del agente estable

```bash
cd morris_competition
python benchmark_grp1_final.py
```

### Generar self-play inicial

```bash
cd morris_competition
python training/self_play.py
```

### Entrenar red inicial

```bash
cd morris_competition
python training/train.py
```

### Evaluar red inicial

```bash
cd morris_competition
python training/evaluate_model.py
```

### Generar self-play AlphaZero-like

```bash
cd morris_competition
python training/self_play_az.py
```

### Entrenar red AlphaZero-like

```bash
cd morris_competition
python training/train_az.py
```

### Evaluar red AlphaZero-like

```bash
cd morris_competition
python training/evaluate_az_model.py
```

---

## 16. Qué dejar y qué no tocar antes de competencia

### Dejar como agente oficial

```text
morris_competition/agents/GRP1/grp1_agent.py
```

Este es el agente estable que debe competir.

### No reemplazar todavía por AlphaZeroAgent

No cambiar en `load_agents.py`:

```python
from agents.GRP1.grp1_agent import GRP1
```

No reemplazar por:

```python
from agents.GRP1.alphazero_agent import AlphaZeroAgent
```

Motivo:

```text
El agente estable ya fue validado con 100% win rate contra Random.
AlphaZeroAgent es experimental y aún no debe reemplazar al agente competitivo.
```

---

## 17. Qué conservar en el repositorio

Conservar:

```text
morris_competition/
morris_dev/
docs/
ethics/
README.md
requirements.txt
.gitignore
```

`morris_dev/` se conserva como evidencia de desarrollo y comparación histórica.

---

## 18. Qué excluir del ZIP o del repositorio si aplica

No incluir:

```text
.venv/
__pycache__/
.idea/
zip_originales/
*.pyc
```

Si los checkpoints son muy pesados, pueden excluirse del repositorio y regenerarse con:

```bash
python training/self_play.py
python training/train.py
python training/self_play_az.py
python training/train_az.py
```

Para defensa local, se recomienda conservar los checkpoints generados.

---

## 19. Conclusión

El proyecto contiene un agente estable de competencia basado en MCTS y un pipeline AlphaZero-like experimental.

La versión recomendada para competir es:

```text
GRP1 = MCTS básico + captura heurística + prioridad de molino inmediato
```

La arquitectura AlphaZero-like implementada permite demostrar:

```text
PUCT + policy/value network + self-play + entrenamiento con visit policy
```

Sin embargo, por estabilidad competitiva, `AlphaZeroAgent` se mantiene separado del agente final hasta superar benchmarks contra el agente estable.
