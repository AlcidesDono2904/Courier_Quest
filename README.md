# Courier_Quest

## 🗺️ Introducción

"Courier Quest" es un videojuego desarrollado en Python que simula a un repartidor en bicicleta en una ciudad. El objetivo principal es aceptar y completar pedidos para alcanzar una meta de ingresos antes de que termine la jornada laboral simulada. El juego incorpora elementos de gestión de inventario, clima dinámico, reputación y, en esta segunda fase, un **jugador CPU (IA) que compite por las entregas**.

---

## 🎯 Objetivos de Aprendizaje

El proyecto se diseñó para cumplir con los siguientes objetivos de aprendizaje:
* **Implementar y justificar el uso de estructuras de datos lineales y no lineales** (colas, árboles, grafos, colas de prioridad).
* **Implementar algoritmos de decisión y búsqueda adaptados** al contexto del juego.
* **Analizar la eficiencia de distintos enfoques de IA**.
* **Desarrollar un agente autónomo** que se comporte de manera coherente y competitiva.
* **Practicar el manejo de archivos en múltiples formatos** (JSON, texto, binario).
* **Aplicar algoritmos de ordenamiento** en escenarios reales.
* **Desarrollar un videojuego con Python** y una librería de desarrollo de juegos (Pygame).
* **Integrar un API real** y gestionar un sistema de caché para trabajar en modo offline.
* **Diseñar un bucle de juego consistente** con reglas cuantificables (clima, reputación, resistencia).

---

## 🎮 Jugabilidad

### El Repartidor y el Mundo de Juego
El jugador controla un repartidor en una ciudad representada por una cuadrícula de calles, edificios y parques. El rendimiento del repartidor está influenciado por varias variables interconectadas:
* **Resistencia:** Una barra de 0 a 100 que disminuye con el movimiento, especialmente con peso extra o clima adverso.
* **Reputación:** Comienza en 70/100 y sube o baja según la puntualidad de las entregas. Una reputación alta (≥90) otorga un 5% de pago extra, mientras que una reputación por debajo de 20 resulta en una derrota inmediata.
* **Clima:** El clima cambia automáticamente cada 45-60 segundos siguiendo una cadena de Markov. El clima adverso reduce la velocidad y aumenta el consumo de resistencia.

### El Rival de IA
El juego incluye un jugador controlado por **Inteligencia Artificial (IA)** que compite por las entregas y puede ser configurado en **tres niveles de dificultad**. El rival tiene su propia barra de resistencia, reputación y capacidad de carga, y recibe la misma información del mundo que el jugador humano.

---

### Gestión de Pedidos
Los pedidos se presentan en dos categorías: normales (prioridad 0) o con prioridad (N). Los pedidos aceptados se almacenan en el inventario, que es una lista que puede recorrerse hacia adelante o hacia atrás para decidir el orden de entrega.

---

### Condiciones de Fin de Juego
* **Victoria:** Alcanzar la meta de ingresos antes de que acabe el tiempo de juego.
* **Derrota:** La reputación del repartidor cae por debajo de 20, o la jornada laboral finaliza sin haber cumplido la meta.

---

## ⚙️ Estructuras de Datos y Algoritmos

El proyecto utiliza diversas estructuras de datos y algoritmos para implementar su lógica:

* **Listas Doblemente Enlazadas** (`src/logic/inventory.py`):
    * **Justificación:** Ideal para el inventario de pedidos, permitiendo una **navegación fluida bidireccional** (`view_next_order`, `view_prev_order`) en **O(1)** y una eficiente inserción/eliminación.
    * **Complejidad Algorítmica:** Inserción/Eliminación: **O(1)**. Navegación secuencial: **O(N)**.

* **Pila (implementada con una lista de Python)** (`src/logic/game_state.py`):
    * **Justificación:** Estructura **LIFO** (Último en Entrar, Primero en Salir) perfecta para la función de **"deshacer"** (`undo`), revirtiendo la última acción de movimiento.
    * **Complejidad Algorítmica:** Operaciones `push` y `pop`: **O(1)**.

* **Matriz** (`src/logic/city.py`):
    * **Justificación:** Representación intuitiva 2D de la ciudad, permitiendo un **acceso directo a cualquier celda** por sus coordenadas (x, y).
    * **Complejidad Algorítmica:** Acceso a elemento: **O(1)**.

* **Colas de Prioridad (Min-Heap)**:
    * **Justificación:** Esencial para el algoritmo A\*, permitiendo la extracción eficiente del nodo con el menor costo total (`f_score`), lo que acelera la búsqueda de ruta óptima.
    * **Complejidad Algorítmica:** Inserción (`heappush`) y Extracción (`heappop`): **O(log N)**.

* **Algoritmos de Ordenamiento (Timsort)**:
    * **Justificación:** Se utiliza el Timsort nativo de Python para ordenar el inventario por prioridad o fecha límite y mantener la tabla de puntajes ordenada.
    * **Complejidad Algorítmica:** **O(N log N)** en todos los casos, garantizando un rendimiento eficiente.

### 🤖 Algoritmos de Inteligencia Artificial (IA)

Se implementaron tres estrategias de búsqueda distintas para el rival de la CPU, adaptadas a los objetivos de cada nivel de dificultad:

| Dificultad | Algoritmo Elegido | Justificación y Comparación | Implementación Clave |
| :--- | :--- | :--- | :--- |
| **Fácil** | **Random Walk / Random Choice** | **Justificación**: Cumple el objetivo de tener una **lógica probabilística simple** y un comportamiento básico. No requiere estructuras complejas ni análisis de costos. | El movimiento (`EasyStrategy.next_move`) es **aleatorio** entre las direcciones adyacentes válidas, y la selección de pedidos se hace con `random.choices`. |
| **Medio** | **Greedy Best-First Search** (GBFS) | **Justificación**: Simula una IA que **evalúa estados** y tiene **anticipación limitada**, priorizando el mejor resultado inmediato (el más "ambicioso"). **Función Clave**: La decisión se basa en la heurística: $score = \alpha(\text{pago}) - \beta(\text{distancia}) - \gamma(\text{clima})$. | Implementado en `MediumStrategy` utilizando `heapq` (cola de prioridad) donde la prioridad del nodo es únicamente su **distancia heurística** al objetivo (`_heuristic`), ignorando el costo real recorrido (`g_score`). |
| **Difícil** | **Algoritmo A\*** (A estrella) | **Justificación**: Es la mejor opción para la **planificación de ruta óptima** en un grafo ponderado. **Superioridad**: Es más eficiente que **Dijkstra** porque su heurística (Manhattan) dirige la búsqueda hacia la meta, y es superior a **BFS** y **DFS** porque considera las **ponderaciones** (costos de la superficie y el clima). | El mapa se modela como un **grafo ponderado** (el peso de la superficie y el clima afectan el costo de la arista). `HardStrategy._find_path` utiliza una **Cola de Prioridad** y calcula el costo total $f(n) = g(n) + h(n)$ para asegurar la ruta más corta. |

---

## 💾 Persistencia de Datos

### Modo Offline y Caché
La información del mundo de juego (mapa, pedidos, clima) se obtiene a través de un API. Para soportar el modo offline, el juego implementa un proxy que prioriza la carga de datos en el siguiente orden: API en línea, caché local, y archivos de respaldo locales.

### Guardado de Partida
El juego permite guardar y cargar partidas en **3 ranuras diferentes**, utilizando archivos binarios. También se guarda el historial de movimientos para la función de deshacer.

---

## 💻 Instalación y Ejecución

Para ejecutar el juego, siga estos pasos:
1.  Asegúrese de tener Python 3.11 o superior instalado.
2.  Instale las dependencias del proyecto utilizando `pip`: `pip install -r requirements.txt`.
3.  Ejecute el script de configuración, el cual creará los directorios necesarios y verificará las dependencias: `./src/config/setup.sh`.
4.  Ejecute el juego con el siguiente comando: `python -m src.main`.

---

## ✍️ Autores

Mariela Orozco Rayo

Rodney Morales Mora

Alcides Jiménez Carrillo
