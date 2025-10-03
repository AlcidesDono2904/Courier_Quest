import random


class City:
    """Representa el mapa de la ciudad."""
    
    def __init__(self, map_data):
        self.version = map_data.get("version")
        self.width = map_data.get("width")
        self.height = map_data.get("height")
        self.tiles = map_data.get("tiles")
        self.legend = map_data.get("legend")
        self.goal = map_data.get("goal")
    
    def get_tile(self, x, y):
        """Obtiene el tile en coordenadas (x, y)."""
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None
    
    def get_surface_weight(self, x, y):
        """Obtiene peso de superficie del tile."""
        tile = self.get_tile(x, y)
        if tile and tile in self.legend:
            return self.legend[tile].get("surface_weight", 1.0)
        return 1.0
    
    def is_blocked(self, x, y):
        """Verifica si un tile está bloqueado."""
        tile = self.get_tile(x, y)
        if tile and tile in self.legend:
            return self.legend[tile].get("blocked", False)
        return True
    
    def get_random_walkable_position(self):
        """Retorna posición aleatoria caminable (calle o parque)."""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if not self.is_blocked(x, y):
                return [x, y]
            
            attempts += 1
        
        # Fallback: buscar la primera posición válida
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_blocked(x, y):
                    return [x, y]
        
        return [0, 0]


class OrderManager:
    """Gestiona pedidos disponibles del API."""
    
    def __init__(self, orders_data):
        self.all_orders = orders_data
        self.available_orders = []
        self.released_ids = set()
    
    def update_available(self, elapsed_time):
        """Actualiza pedidos disponibles según release_time."""
        for order in self.all_orders:
            order_id = order.get("id")
            release = order.get("release_time", 0)
            
            if release <= elapsed_time and order_id not in self.released_ids:
                self.available_orders.append(order)
                self.released_ids.add(order_id)
    
    def get_available(self):
        """Retorna pedidos disponibles."""
        return self.available_orders
    
    def remove_order(self, order_id):
        """Remueve pedido aceptado de disponibles."""
        self.available_orders = [
            o for o in self.available_orders 
            if o.get("id") != order_id
        ]