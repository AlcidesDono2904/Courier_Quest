import pygame
import json


class Map:
    def __init__(self, map_data=None):
        """
        Inicializa el mapa del juego.
        
        Args:
            map_data (dict): Datos del mapa desde el API o archivo JSON
        """
        if map_data:
            self.load_from_data(map_data)
        else:
            self.width = 0
            self.height = 0
            self.tiles = []
            self.legend = {}
            self.goal = 0
            
        self.cell_size = 32  # Tamaño de cada celda en píxeles
        self.colors = {
            "C": (128, 128, 128),  # Calle - Gris
            "B": (139, 69, 19),    # Edificio - Marrón
            "P": (34, 139, 34),    # Parque - Verde
            "default": (200, 200, 200)  # Color por defecto
        }
        
    def load_from_data(self, map_data):
        """
        Carga los datos del mapa desde un diccionario.
        
        Args:
            map_data (dict): Estructura de datos del mapa
        """
        self.width = map_data.get("width", 0)
        self.height = map_data.get("height", 0)
        self.tiles = map_data.get("tiles", [])
        self.legend = map_data.get("legend", {})
        self.goal = map_data.get("goal", 0)
        
    def load_from_file(self, filename):
        """
        Carga el mapa desde un archivo JSON.
        
        Args:
            filename (str): Ruta del archivo JSON
        """
        try:
            with open(filename, 'r') as f:
                map_data = json.load(f)
                self.load_from_data(map_data)
                print(f"Mapa cargado desde {filename}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {filename}")
        except json.JSONDecodeError:
            print(f"Error: Formato JSON inválido en {filename}")
    
    def get_tile_type(self, x, y):
        """
        Obtiene el tipo de tile en las coordenadas especificadas.
        
        Args:
            x (int): Coordenada X (columna)
            y (int): Coordenada Y (fila)
            
        Returns:
            str: Tipo de tile o None si está fuera de límites
        """
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None
    
    def get_tile_properties(self, tile_type):
        """
        Obtiene las propiedades de un tipo de tile desde la leyenda.
        
        Args:
            tile_type (str): Tipo de tile (ej: "C", "B", "P")
            
        Returns:
            dict: Propiedades del tile
        """
        return self.legend.get(tile_type, {})
    
    def is_walkable(self, x, y):
        """
        Verifica si una celda es caminable (no bloqueada).
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            bool: True si es caminable, False si no
        """
        tile_type = self.get_tile_type(x, y)
        if tile_type is None:
            return False
            
        tile_props = self.get_tile_properties(tile_type)
        return not tile_props.get("blocked", False)
    
    def get_surface_weight(self, x, y):
        """
        Obtiene el peso de superficie de una celda para cálculos de velocidad.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            float: Peso de superficie (1.0 por defecto)
        """
        tile_type = self.get_tile_type(x, y)
        if tile_type is None:
            return 1.0
            
        tile_props = self.get_tile_properties(tile_type)
        return tile_props.get("surface_weight", 1.0)
    
    def get_valid_neighbors(self, x, y):
        """
        Obtiene las celdas vecinas válidas (caminables) de una posición.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            list: Lista de tuplas (x, y) de vecinos válidos
        """
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Arriba, abajo, derecha, izquierda
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_walkable(new_x, new_y):
                neighbors.append((new_x, new_y))
                
        return neighbors
    
    def world_to_grid(self, world_x, world_y):
        """
        Convierte coordenadas del mundo a coordenadas de cuadrícula.
        
        Args:
            world_x (int): Coordenada X en píxeles
            world_y (int): Coordenada Y en píxeles
            
        Returns:
            tuple: (grid_x, grid_y)
        """
        return world_x // self.cell_size, world_y // self.cell_size
    
    def grid_to_world(self, grid_x, grid_y):
        """
        Convierte coordenadas de cuadrícula a coordenadas del mundo.
        
        Args:
            grid_x (int): Coordenada X de la cuadrícula
            grid_y (int): Coordenada Y de la cuadrícula
            
        Returns:
            tuple: (world_x, world_y) en píxeles
        """
        return grid_x * self.cell_size, grid_y * self.cell_size
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """
        Dibuja el mapa en la pantalla.
        
        Args:
            screen: Superficie de pygame donde dibujar
            camera_x (int): Offset de cámara X
            camera_y (int): Offset de cámara Y
        """
        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile_type in enumerate(row):
                # Calcular posición en pantalla
                x = col_idx * self.cell_size - camera_x
                y = row_idx * self.cell_size - camera_y
                
                # Solo dibujar si está visible en pantalla
                if -self.cell_size <= x <= screen.get_width() and -self.cell_size <= y <= screen.get_height():
                    color = self.colors.get(tile_type, self.colors["default"])
                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    pygame.draw.rect(screen, color, rect)
                    
                    # Dibujar borde
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                    
                    # Dibujar letra del tipo de tile
                    font = pygame.font.Font(None, 24)
                    text = font.render(tile_type, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    screen.blit(text, text_rect)
    
    def find_spawn_position(self):
        """
        Encuentra una posición válida para hacer spawn del jugador.
        
        Returns:
            tuple: (x, y) en coordenadas de cuadrícula, o (0, 0) si no encuentra
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.is_walkable(x, y):
                    return x, y
        return 0, 0
    
    def find_positions_by_type(self, tile_type):
        """
        Encuentra todas las posiciones de un tipo de tile específico.
        
        Args:
            tile_type (str): Tipo de tile a buscar
            
        Returns:
            list: Lista de tuplas (x, y) con las posiciones
        """
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.get_tile_type(x, y) == tile_type:
                    positions.append((x, y))
        return positions
    
    def get_distance(self, x1, y1, x2, y2):
        """
        Calcula la distancia Manhattan entre dos puntos.
        
        Args:
            x1, y1: Coordenadas del primer punto
            x2, y2: Coordenadas del segundo punto
            
        Returns:
            int: Distancia Manhattan
        """
        return abs(x1 - x2) + abs(y1 - y2)
    
    def save_to_file(self, filename):
        """
        Guarda el mapa actual a un archivo JSON.
        
        Args:
            filename (str): Ruta del archivo donde guardar
        """
        map_data = {
            "version": "1.0",
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "legend": self.legend,
            "goal": self.goal
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(map_data, f, indent=2)
                print(f"Mapa guardado en {filename}")
        except Exception as e:
            print(f"Error al guardar el mapa: {e}")


# Ejemplo de uso y testing
if __name__ == "__main__":
    # Crear un mapa de ejemplo
    example_map_data = {
        "version": "1.0",
        "width": 10,
        "height": 8,
        "tiles": [
            ["C", "C", "C", "B", "B", "C", "C", "C", "B", "B"],
            ["C", "P", "C", "C", "B", "C", "P", "C", "C", "B"],
            ["B", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
            ["C", "C", "B", "C", "C", "C", "B", "C", "C", "C"],
            ["C", "C", "C", "C", "P", "C", "C", "C", "B", "C"],
            ["B", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
            ["C", "C", "B", "C", "C", "C", "B", "C", "C", "P"],
            ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C"]
        ],
        "legend": {
            "C": {"name": "calle", "surface_weight": 1.00},
            "B": {"name": "edificio", "blocked": True},
            "P": {"name": "parque", "surface_weight": 0.95}
        },
        "goal": 3000
    }
    
    # Crear instancia del mapa
    game_map = Map(example_map_data)
    
    # Probar funcionalidades
    print(f"Dimensiones del mapa: {game_map.width}x{game_map.height}")
    print(f"Meta de ingresos: {game_map.goal}")
    print(f"Posición de spawn: {game_map.find_spawn_position()}")
    print(f"¿Es caminable (2,2)?: {game_map.is_walkable(2, 2)}")
    print(f"¿Es caminable (3,0)?: {game_map.is_walkable(3, 0)}")  # Edificio
    print(f"Peso de superficie en (1,1): {game_map.get_surface_weight(1, 1)}")  # Parque
    print(f"Vecinos válidos de (5,3): {game_map.get_valid_neighbors(5, 3)}")