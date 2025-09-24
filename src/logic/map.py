import heapq
import player
import weather
from sys import path
path.append('..\\Courier_Quest-1')
from src.config.config import *

# --- CLASE PARA EL MAPA Y PATHFINDING (A*) ---
class GameMap:
    def __init__(self, api_response):
        # Extraemos el diccionario correcto que está dentro de la clave 'data'
        map_data = api_response['data']
        
        # Ahora usamos ese diccionario para obtener los valores
        self.width = map_data['width']
        self.height = map_data['height']
        self.tiles = map_data['tiles']
        self.legend = map_data['legend']
        self.goal = map_data['goal']

    def is_blocked(self, x, y):
        tile_char = self.tiles[y][x]
        return self.legend.get(tile_char, {}).get('blocked', False)

    def get_surface_weight(self, x, y):
        tile_char = self.tiles[y][x]
        return self.legend.get(tile_char, {}).get('surface_weight', 1.0)

    def a_star_pathfinding(self, start, end):
        # Implementación del algoritmo A*
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = { (r, c): float('inf') for r in range(self.height) for c in range(self.width) }
        g_score[start] = 0
        f_score = { (r, c): float('inf') for r in range(self.height) for c in range(self.width) }
        f_score[start] = abs(start[0] - end[0]) + abs(start[1] - end[1])

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.height:
                    if self.is_blocked(neighbor[0], neighbor[1]):
                        continue
                    
                    tentative_g_score = g_score[current] + 1 # Costo de 1 por moverse a un vecino
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                        if neighbor not in [i[1] for i in open_set]:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return [] # No se encontró ruta


