## Prueba 1: MCTS básico vs Random

Fecha: 26/04/2026  
Carpeta usada: morris_dev  
Archivo del agente: morris_dev/agents/mcts_agent.py  
Archivo de prueba: morris_dev/test_mcts_vs_random.py  
Tiempo MCTS por turno: 0.2 s  
Partidas por serie: 10  
Total de partidas: 20  

### Resultado

- Victorias de MCTS: 20 / 20
- Victorias de Random: 0 / 20
- Empates / sin ganador: 0
- Win rate MCTS: 100%

### Detalle

- Serie 1: MCTS como jugador 1 → 10W / 0L / 0D
- Serie 2: MCTS como jugador 2 → 10W / 0L / 0D

### Conclusión inicial

El MCTS básico supera claramente al agente aleatorio en esta prueba inicial. Además, ganó tanto jugando primero como jugando segundo, lo cual reduce el sesgo por orden de turno. Sin embargo, se necesita una prueba adicional con más partidas y un control Random vs Random para validar que el benchmark no esté sesgado.
## Prueba 2: Benchmark completo MCTS básico vs Random

Fecha: 26/04/2026  
Carpeta usada: morris_dev  
Archivo del agente: morris_dev/agents/mcts_agent.py  
Archivo de benchmark: morris_dev/benchmark_agents.py  

### Objetivo

Validar que el agente MCTS básico supera al agente aleatorio y comprobar que el benchmark no favorece artificialmente a un jugador.

### Sección 1: Random vs Random

Total de partidas: 20  

- Victorias Player 1: 8
- Victorias Player 2: 9
- Empates / límite: 3

Conclusión: el entorno de prueba no muestra un sesgo fuerte hacia Player 1 o Player 2.

### Sección 2: MCTS vs Random con TIME_LIMIT = 0.20 s

Total de partidas: 100  

- MCTS como Player 1: 50 victorias / 50 partidas
- MCTS como Player 2: 50 victorias / 50 partidas
- Victorias totales de MCTS: 100 / 100
- Victorias de Random: 0 / 100
- Empates: 0
- Win rate MCTS: 100%

### Sección 3: Comparación por tiempo de búsqueda

| Tiempo por turno | Partidas | Victorias MCTS | Victorias Random | Empates | Win rate MCTS |
|---|---:|---:|---:|---:|---:|
| 0.05 s | 20 | 20 | 0 | 0 | 100% |
| 0.10 s | 20 | 20 | 0 | 0 | 100% |
| 0.20 s | 20 | 20 | 0 | 0 | 100% |

### Resultado global

Tiempo total del benchmark: 1026 s, aproximadamente 17.1 minutos.

El agente MCTS básico superó completamente al agente aleatorio en todas las configuraciones probadas. Esto confirma que la implementación de selección, expansión, simulación y retropropagación funciona correctamente y produce decisiones superiores al azar.
## Prueba 3: MCTS con heurística vs Random

Fecha: 26/04/2026  
Versión: Etapa 2 - MCTS con heurística  
Archivo activo: morris_dev/agents/mcts_agent.py  

### Prueba rápida

Comando:

```powershell
python test_mcts_vs_random.py
python benchmark_agents.py
## Prueba 4: Comparación V1 MCTS básico vs V2 MCTS con heurística

Fecha: 26/04/2026  
Archivo de prueba: morris_dev/benchmark_v1_vs_v2.py  
Tiempo por turno: 0.2 s  
Total de partidas: 40  

### Resultado

| Serie | Partidas | Victorias V2 | Victorias V1 | Empates | WR V2 | WR V1 |
|---|---:|---:|---:|---:|---:|---:|
| V1(P1) vs V2(P2) | 20 | 3 | 17 | 0 | 15% | 85% |
| V2(P1) vs V1(P2) | 20 | 3 | 17 | 0 | 15% | 85% |
| Total | 40 | 6 | 34 | 0 | 15% | 85% |

### Conclusión

La versión V2 con heurística no mejoró al agente. Aunque mantenía buen rendimiento contra Random, perdió claramente contra V1. Esto indica que la heurística o el rollout guiado introdujeron decisiones peores, mayor costo computacional o una evaluación incorrecta de los estados. Por esta razón, V1 se mantiene como versión estable del agente.
## Prueba 5: Comparación V1 MCTS básico vs V3 con captura heurística

Fecha: 26/04/2026  
Archivo de prueba: morris_dev/benchmark_v1_vs_v3.py  
Tiempo por turno: 0.2 s  
Total de partidas: 40  

### Resultado

| Serie | Partidas | Victorias V3 | Victorias V1 | Empates | WR V3 | WR V1 |
|---|---:|---:|---:|---:|---:|---:|
| V1(P1) vs V3(P2) | 20 | 8 | 12 | 0 | 40% | 60% |
| V3(P1) vs V1(P2) | 20 | 10 | 10 | 0 | 50% | 50% |
| Total | 40 | 18 | 22 | 0 | 45% | 55% |

### Conclusión

La versión V3, que solo modificó la decisión de captura, no mostró una mejora clara sobre V1. El rendimiento fue similar, pero V1 obtuvo una ventaja ligera en el total combinado. Por esta razón, se mantiene V1 como versión estable principal.
## Benchmark rápido — GRP1 MCTS vs GRP2 Random

Configuración:

| Parámetro | Valor |
|---|---:|
| Partidas por lado | 5 |
| Total de partidas | 10 |
| MAX_TURNS | 120 |
| Oponente | GRP2 Random |

Resultados:

| Serie | Partidas | Victorias GRP1 | Victorias GRP2 | Empates | Win rate GRP1 |
|---|---:|---:|---:|---:|---:|
| GRP1(P1) vs GRP2(P2) | 5 | 3 | 0 | 2 | 60% |
| GRP2(P1) vs GRP1(P2) | 5 | 3 | 0 | 2 | 60% |
| Total | 10 | 6 | 0 | 4 | 60% |

Conclusión:

GRP1 supera al agente aleatorio con ventaja moderada y no registró derrotas en esta muestra. Sin embargo, el número de empates indica que el agente necesita mejorar su capacidad de cerrar partidas.


## Benchmark rápido final — GRP1 MCTS vs GRP2 Random

### Configuración

| Parámetro | Valor |
|---|---:|
| Partidas por lado | 5 |
| Total de partidas | 10 |
| MAX_TURNS | 120 |
| Oponente | GRP2 Random |
| Plataforma | morris_competition |
| Agente evaluado | GRP1 |

### Resultados

| Serie | Partidas | Victorias GRP1 | Victorias GRP2 | Empates | Win rate GRP1 |
|---|---:|---:|---:|---:|---:|
| GRP1(P1) vs GRP2(P2) | 5 | 5 | 0 | 0 | 100% |
| GRP2(P1) vs GRP1(P2) | 5 | 5 | 0 | 0 | 100% |
| Total | 10 | 10 | 0 | 0 | 100% |

### Conclusión

GRP1 superó claramente al agente aleatorio en la prueba rápida final. El agente ganó todas las partidas tanto jugando como Player 1 como jugando como Player 2.

La mejora aplicada al agente redujo los empates observados en el benchmark anterior. En particular, la priorización de molinos inmediatos y la heurística de captura permitieron cerrar partidas con mayor efectividad.
## Benchmark medio final — GRP1 MCTS vs GRP2 Random

### Configuración

| Parámetro | Valor |
|---|---:|
| Partidas por lado | 10 |
| Total de partidas | 20 |
| MAX_TURNS | 150 |
| Oponente | GRP2 Random |
| Plataforma | `morris_competition` |
| Agente evaluado | `GRP1` |

### Resultados

| Serie | Partidas | Victorias GRP1 | Victorias GRP2 | Empates | Win rate GRP1 | Tiempo |
|---|---:|---:|---:|---:|---:|---:|
| GRP1(P1) vs GRP2(P2) | 10 | 10 | 0 | 0 | 100% | 18.1s |
| GRP2(P1) vs GRP1(P2) | 10 | 10 | 0 | 0 | 100% | 28.7s |
| Total | 20 | 20 | 0 | 0 | 100% | 46.8s |

### Conclusión

GRP1 superó claramente al agente aleatorio. El agente ganó todas las partidas tanto jugando como Player 1 como jugando como Player 2, sin empates ni derrotas.

La versión final seleccionada es:

`GRP1 = MCTS básico + captura heurística + prioridad de molino inmediato`.