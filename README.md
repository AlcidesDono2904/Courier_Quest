# Courier_Quest

## 🗺️ Introducción

"Courier Quest" es un videojuego desarrollado en Python que simula a un repartidor en bicicleta en una ciudad. El objetivo principal es aceptar y completar pedidos para alcanzar una meta de ingresos antes de que termine la jornada laboral simulada. El juego incorpora elementos de gestión de inventario, clima dinámico y reputación, haciendo que la experiencia de juego sea un desafío estratégico.

## 🎯 Objetivos de Aprendizaje

El proyecto se diseñó para cumplir con los siguientes objetivos de aprendizaje:
* **Implementar y justificar el uso de estructuras de datos lineales**.
* **Practicar el manejo de archivos en múltiples formatos (JSON, texto, binario)**.
* **Aplicar algoritmos de ordenamiento en escenarios reales**.
* **Desarrollar un videojuego con Python y una librería de desarrollo de juegos(en este caso elegimos Pygame)**.
* **Integrar un API real y gestionar un sistema de caché para trabajar en modo offline**.
* **Diseñar un bucle de juego consistente con reglas cuantificables (clima, reputación, resistencia)**.

---

## 🎮 Jugabilidad

### El Repartidor y el Mundo de Juego
El jugador controla un repartidor en una ciudad representada por una cuadrícula de calles, edificios y parques. El rendimiento del repartidor está influenciado por varias variables interconectadas:
* **Resistencia:** Una barra de 0 a 100 que disminuye con el movimiento, especialmente con peso extra o clima adverso. Si llega a cero, el jugador se agota y no puede moverse hasta recuperarse al 30%.
* **Reputación:** Comienza en 70/100 y sube o baja según la puntualidad de las entregas y las acciones del jugador. Una reputación alta (≥90) otorga un 5% de pago extra en los pedidos, mientras que una reputación por debajo de 20 resulta en una derrota inmediata.
* **Clima:** El clima cambia automáticamente cada 45-60 segundos siguiendo una cadena de Markov. La transición entre climas es progresiva, para que los cambios se sientan naturales. El clima adverso reduce la velocidad y aumenta el consumo de resistencia.

---

### Gestión de Pedidos
Los pedidos se presentan en dos categorías: normales (prioridad 0) o con prioridad (N). El jugador puede aceptar o rechazar pedidos, pero solo puede cargar una cantidad máxima de peso. Los pedidos aceptados se almacenan en el inventario, que es una lista que puede recorrerse hacia adelante o hacia atrás para decidir el orden de entrega. Además, el inventario puede ordenarse por hora de entrega o por prioridad.

---

### Condiciones de Fin de Juego
* **Victoria:** Alcanzar la meta de ingresos antes de que acabe el tiempo de juego.
* **Derrota:** La reputación del repartidor cae por debajo de 20, o la jornada laboral finaliza sin haber cumplido la meta.

---

## ⚙️ Estructuras de Datos y Algoritmos

El proyecto utiliza diversas estructuras de datos y algoritmos para implementar su lógica:

* **Listas Doblemente Enlazadas** (`src/logic/inventory.py`):
    * **Justificación:** Se utiliza una lista doblemente enlazada para el inventario de pedidos del jugador. Esta estructura es ideal para permitir una navegación fluida hacia adelante y hacia atrás a través de los pedidos aceptados (`view_next_order`, `view_prev_order`). También es eficiente para añadir y eliminar pedidos, ya que no requiere reajustar los índices de otros elementos.
    * **Complejidad Algorítmica:** La inserción y eliminación de nodos tiene una complejidad promedio de **O(1)**. La navegación secuencial es de **O(N)**, donde N es el número de pedidos.

* **Pila (implementada con una lista de Python)** (`src/logic/game_state.py`):
    * **Justificación:** Una pila es la estructura de datos más adecuada para la función de "deshacer" o `undo`, ya que opera bajo el principio LIFO (Último en Entrar, Primero en Salir). Esto permite al jugador revertir la última acción realizada de manera eficiente.
    * **Complejidad Algorítmica:** Las operaciones de `push` (añadir un estado) y `pop` (deshacer) en una lista de Python tienen una complejidad de tiempo promedio de **O(1)**.

* **Diccionarios** (`src/logic/city.py`, `src/logic/weather.py`):
    * **Justificación:** Se utilizan para almacenar datos de configuración y mapeos, como la leyenda del mapa (`legend`) y las transiciones de la cadena de Markov para el clima. Permiten un acceso directo y rápido a la información a través de una clave.
    * **Complejidad Algorítmica:** Las operaciones de búsqueda, inserción y eliminación tienen una complejidad de tiempo promedio de **O(1)**.

* **Matriz** (`src/logic/city.py`):
    * **Justificación:** La ciudad se representa como una matriz 2D, lo que proporciona una forma intuitiva de modelar el mapa del juego. Esta estructura permite un acceso directo a cualquier celda del mapa a través de sus coordenadas (`x`, `y`).
    * **Complejidad Algorítmica:** El acceso a un elemento por sus coordenadas es de **O(1)**. Las operaciones que requieren recorrer el mapa completo, como el renderizado, tienen una complejidad de **O(W\*H)**, donde W es el ancho y H es la altura del mapa.

* **Algoritmos de Ordenamiento:**
    * **Justificación:** El inventario puede ordenarse por prioridad o fecha límite, y la tabla de puntajes debe guardarse de forma ordenada. Para esto, se utiliza el método de ordenamiento integrado de Python, que es Timsort, y la función `sort_inventory` se utiliza para ordenar el inventario in-place.
    * **Complejidad Algorítmica:** Timsort tiene una complejidad de tiempo de **O(N log N)** en el mejor, promedio y peor de los casos, lo que garantiza un rendimiento eficiente incluso con un número moderado de elementos.

---

## 💾 Persistencia de Datos

### Modo Offline y Caché
La información del mundo de juego (mapa, pedidos, clima) se obtiene a través de un API. Para soportar el modo offline, el juego implementa un proxy que prioriza la carga de datos en el siguiente orden:
1.  API en línea.
2.  Caché local (`/api_cache/`).
3.  Archivos de respaldo locales (`/data/`).

### Guardado de Partida
El juego permite guardar y cargar partidas en 3 ranuras diferentes, utilizando archivos binarios. También se guarda el historial de movimientos para poder deshacer `N` cantidad de pasos. Los puntajes se guardan en un archivo JSON ordenado de mayor a menor.

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

