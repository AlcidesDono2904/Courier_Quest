import requests
import json
from pathlib import Path
import src.config.config as config
from .weather import Weather


class Proxy:
    """Singleton proxy para manejar peticiones al API."""
    
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Proxy, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.base_url = config.URL
        self.offline = False
        Path("api_cache").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
        try:
            result = requests.get(f"{self.base_url}healthz", timeout=5)
            if result.status_code != 200:
                self.offline = True
                print("API no disponible. Modo offline activado.")
        except requests.RequestException:
            self.offline = True
            print("Sin conexión al API. Modo offline activado.")
        
        self._initialized = True

    def _load_cache(self, filename):
        """Carga datos desde caché."""
        try:
            with open(f"api_cache/{filename}", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            with open(f"data/{filename}", 'r') as f:
                return json.load(f)

    def _save_cache(self, filename, data):
        """Guarda datos en caché."""
        with open(f"api_cache/{filename}", 'w') as f:
            json.dump(data, f, indent=2)

    def get_weather(self):
        """Obtiene datos de clima."""
        if not self.offline:
            try:
                result = requests.get(f"{self.base_url}city/weather", timeout=5)
                if result.status_code == 200:
                    data = result.json()
                    self._save_cache("weather.json", data)
                else:
                    data = self._load_cache("weather.json")
            except requests.RequestException:
                data = self._load_cache("weather.json")
        else:
            data = self._load_cache("weather.json")
        
        data = data.get("data", {})
        initial_condition = data.get("initial", {}).get("condition", "clear")
        transition = data.get("transition", {})
        
        return Weather(initial_state=initial_condition, transition=transition)

    def get_map(self):
        """Obtiene datos del mapa."""
        if not self.offline:
            try:
                result = requests.get(f"{self.base_url}city/map", timeout=5)
                if result.status_code == 200:
                    data = result.json()
                    self._save_cache("ciudad.json", data)
                else:
                    data = self._load_cache("ciudad.json")
            except requests.RequestException:
                data = self._load_cache("ciudad.json")
        else:
            data = self._load_cache("ciudad.json")
        
        return data.get("data", data)

    def get_jobs(self):
        """Obtiene datos de pedidos y valida posiciones."""
        if not self.offline:
            try:
                result = requests.get(f"{self.base_url}city/jobs", timeout=5)
                if result.status_code == 200:
                    data = result.json()
                    self._save_cache("pedidos.json", data)
                else:
                    data = self._load_cache("pedidos.json")
            except requests.RequestException:
                data = self._load_cache("pedidos.json")
        else:
            data = self._load_cache("pedidos.json")
        
        jobs = data.get("data", data)
        
        # Validar y corregir posiciones de pedidos
        map_data = self.get_map()
        from .city import City
        city = City(map_data)
        
        for job in jobs:
            pickup = job.get("pickup", [0, 0])
            dropoff = job.get("dropoff", [0, 0])
            
            # Si pickup está bloqueado, buscar posición válida cercana
            if city.is_blocked(pickup[0], pickup[1]):
                job["pickup"] = self._find_nearby_walkable(city, pickup[0], pickup[1])
            
            # Si dropoff está bloqueado, buscar posición válida cercana
            if city.is_blocked(dropoff[0], dropoff[1]):
                job["dropoff"] = self._find_nearby_walkable(city, dropoff[0], dropoff[1])
        
        return jobs
    
    def _find_nearby_walkable(self, city, x, y):
        """Encuentra la posición caminable más cercana."""
        # Buscar en espiral desde la posición original
        for radius in range(1, 10):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    new_x = x + dx
                    new_y = y + dy
                    
                    if 0 <= new_x < city.width and 0 <= new_y < city.height:
                        if not city.is_blocked(new_x, new_y):
                            return [new_x, new_y]
        
        # Si no encuentra, usar posición aleatoria
        return city.get_random_walkable_position()