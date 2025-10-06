# Courier_Quest

Courier Quest
🗺️ Introducción
"Courier Quest" es un videojuego desarrollado en Python que simula a un repartidor en bicicleta en una ciudad. El objetivo principal es aceptar y completar pedidos para alcanzar una meta de ingresos antes de que termine la jornada laboral simulada. El juego incorpora elementos de gestión de inventario, clima dinámico y reputación, haciendo que la experiencia de juego sea un desafío estratégico.

🎯 Objetivos de Aprendizaje
El proyecto se diseñó para cumplir con los siguientes objetivos de aprendizaje:

Implementar y justificar el uso de estructuras de datos lineales.

Practicar el manejo de archivos en múltiples formatos (JSON, texto, binario).

Aplicar algoritmos de ordenamiento en escenarios reales.

Desarrollar un videojuego con Python y una librería de desarrollo de juegos.

Integrar un API real y gestionar un sistema de caché para trabajar en modo offline.

Diseñar un bucle de juego consistente con reglas cuantificables (clima, reputación, resistencia).

🎮 Jugabilidad
El Repartidor y el Mundo de Juego
El jugador controla un repartidor en una ciudad representada por una cuadrícula de calles, edificios y parques. El rendimiento del repartidor está influenciado por varias variables:

Resistencia: Una barra de 0 a 100 que disminuye con el movimiento, especialmente con peso extra o clima adverso. Si llega a cero, el jugador se agota y debe recuperarse antes de poder moverse de nuevo.

Reputación: Comienza en 70/100 y sube o baja según la puntualidad de las entregas y las acciones del jugador. Una reputación alta (≥90) otorga un 5% de pago extra en los pedidos, mientras que una reputación por debajo de 20 resulta en una derrota inmediata.

Clima: El clima cambia automáticamente y de forma progresiva, afectando la velocidad y el consumo de resistencia.

Gestión de Pedidos
Los pedidos se presentan en dos categorías: normales (prioridad 0) o con prioridad (N). El jugador puede aceptar pedidos, pero debe tener cuidado con el peso, ya que existe un peso máximo que puede transportar. Los pedidos aceptados se almacenan en un inventario y el jugador puede navegar entre ellos.

Condiciones de Fin de Juego

Victoria: Alcanzar la meta de ingresos antes de que acabe el tiempo de juego.

Derrota: La reputación del repartidor cae por debajo de 20, o la jornada laboral finaliza sin haber cumplido la meta de ingresos.

⚙️ Estructuras de Datos y Algoritmos

Listas Doblemente Enlazadas: La clase Inventory utiliza una lista doblemente enlazada para gestionar los pedidos del jugador. Esto permite navegar fácilmente hacia adelante y hacia atrás entre los pedidos (view_next_order, view_prev_order) y reordenar la lista completa de manera eficiente (sort_inventory). El algoritmo de ordenamiento por inserción se utiliza para organizar el inventario por prioridad o fecha límite.

Listas/Arreglos: El mapa de la ciudad se representa como una lista de listas de caracteres (tiles), lo que facilita la búsqueda de ubicaciones y la verificación de colisiones. La clase GameState utiliza una lista para almacenar el historial de estados del juego, lo que permite la funcionalidad de "deshacer" (undo).

Diccionarios: Los diccionarios se usan extensivamente para cargar datos de archivos JSON, como la leyenda del mapa (legend) o la matriz de transición del clima (transition). La clase Weather utiliza un diccionario para representar la cadena de Markov que determina los cambios climáticos en el juego.

Archivos JSON y Binarios: Los puntajes altos se guardan en un archivo JSON y se ordenan de mayor a menor. El estado del juego se guarda en archivos binarios (
.sav) para una carga y guardado rápidos.

💾 Persistencia de Datos
Modo Offline y Caché
La información del mundo de juego (mapa, pedidos, clima) se obtiene a través de un API. Para soportar el modo offline, el juego implementa un proxy que prioriza la carga de datos en el siguiente orden:
API en línea.
Caché local (/api_cache/) si no tiene más de 24 horas.
Archivos de respaldo locales (/data/).

Guardado de Partida
El juego permite guardar y cargar partidas en 3 ranuras diferentes, utilizando archivos binarios. También ofrece una función de guardado automático que usa la primera ranura vacía o sobrescribe la más antigua si todas están llenas.

💻 Instalación y Ejecución
Para ejecutar el juego, siga estos pasos:

Asegúrese de tener Python 3.11 o superior instalado.

Instale las dependencias del proyecto utilizando:

pip install -r requirements.txt
Ejecute el script de configuración, el cual creará los directorios necesarios y verificará las dependencias:

./src/config/setup.sh
Ejecute el juego con el siguiente comando:

python -m src.main
✍️ Autores
Mariela Orozco Rayo 
Rodney Morales Mora
Alcides Jiménez Carrillo
