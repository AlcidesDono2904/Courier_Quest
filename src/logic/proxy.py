# proxy.py
import requests
import json
import os 
from datetime import datetime, timedelta
from sys import path
path.append('..\\Courier_Quest')
import src.config.config as config
from src.logic.weather import Weather
from src.logic.map import Map
from src.logic.order import Order

# Singleton proxy class to manage API requests
class Proxy:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Proxy, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.base_url = config.URL
        # 2. INICIALIZAR DIRECTORIOS
        self.cache_dir = "api_cache"
        self.data_dir = "data"
        self.offline = False
        
        # Crear directorio de caché si no existe
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self._check_api_health()

    def _check_api_health(self):
        """Verifica si el API está disponible."""
        try:
            # Aseguramos que la URL se une correctamente
            result = requests.get(f"{self.base_url.rstrip('/')}/healthz", timeout=5)
            if result.status_code == 200 and result.json().get("ok"):
                self.offline = False
                print("✅ API conectado correctamente.")
            else:
                self._set_offline_mode(f"API healthcheck falló con status {result.status_code}")
        except requests.exceptions.RequestException as e:
            self._set_offline_mode(f"Error de conexión: {e}")

    def _set_offline_mode(self, reason):
        """Configura el modo offline."""
        self.offline = True
        print(f"⚠️ Cambiando a modo offline: {reason}")
    
    # 3. LÓGICA DE DATOS UNIFICADA
    def _get_data(self, endpoint, cache_filename, fallback_filename):
        """
        Método genérico para obtener datos siguiendo la lógica:
        API -> Caché Válido -> Archivo de Respaldo.
        """
        # --- Paso 1: Intentar desde el API ---
        if not self.offline:
            try:
                url = f"{self.base_url.rstrip('/')}/{endpoint}"
                result = requests.get(url, timeout=10)
                if result.status_code == 200:
                    data = result.json()
                    self._save_cache(cache_filename, data)
                    print(f"✔️ Datos de '{endpoint}' cargados desde API.")
                    return data
                else:
                    print(f"❌ Error en API '{endpoint}': Status {result.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de red en '{endpoint}': {e}")
        
        # --- Paso 2: Intentar desde la Caché ---
        cached_data = self._load_cache(cache_filename)
        if cached_data:
            print(f"✔️ Datos de '{endpoint}' cargados desde la caché.")
            return cached_data

        # --- Paso 3: Intentar desde el Archivo de Respaldo ---
        fallback_data = self._load_fallback(fallback_filename)
        if fallback_data:
            print(f"✔️ Datos de '{endpoint}' cargados desde archivo de respaldo.")
            return fallback_data

        print(f"❌ FATAL: No se pudieron cargar los datos para '{endpoint}'.")
        return None

    def _save_cache(self, filename, data):
        """Guarda datos en la caché con timestamp."""
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        cache_path = os.path.join(self.cache_dir, filename)
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def _load_cache(self, filename):
        """Carga datos desde la caché si son recientes (menos de 24h)."""
        cache_path = os.path.join(self.cache_dir, filename)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_content = json.load(f)
            timestamp = datetime.fromisoformat(cache_content['timestamp'])
            if datetime.now() - timestamp < timedelta(hours=24):
                return cache_content['data']
        return None

    def _load_fallback(self, filename):
        """Carga datos de respaldo desde la carpeta data."""
        data_path = os.path.join(self.data_dir, filename)
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return json.load(f)
        return None

    # --- MÉTODOS PÚBLICOS SIMPLIFICADOS ---
    
    def get_map(self) -> Map:
        """Obtiene el mapa del juego."""
        raw_data = self._get_data("city/map", "map.json", "ciudad.json")
        if raw_data:
            map_data = raw_data.get("data", raw_data)
            return Map(map_data)
        return Map(self._get_default_map_data()) # Mapa de emergencia

    def get_weather(self) -> Weather:
        """Obtiene los datos del clima."""
        raw_data = self._get_data("city/weather", "weather.json", "clima.json")
        if raw_data:
            weather_data = raw_data.get("data", raw_data)
            # Asegurarse que la estructura es la esperada antes de acceder
            initial = weather_data.get("initial", {})
            condition = initial.get("condition", "clear")
            transition = weather_data.get("transition", {})
            return Weather(initial_state=condition, transition=transition)
        return Weather(initial_state="clear", transition={}) # Clima de emergencia

    def get_orders(self) -> list[Order]:
        """Obtiene la lista de pedidos."""
        raw_data = self._get_data("city/jobs", "orders.json", "pedidos.json")
        if raw_data:
            orders_list_data = raw_data.get("data", raw_data)
            
            # El API puede envolver los jobs en una clave "jobs"
            if isinstance(orders_list_data, dict) and "jobs" in orders_list_data:
                 orders_list_data = orders_list_data["jobs"]
            
            orders = []
            for order_data in orders_list_data:
                orders.append(Order(**order_data)) # Forma más limpia de crear el objeto
            return orders
        return [] # Lista vacía si todo falla

    def _get_default_map_data(self):
        """Retorna datos de mapa por defecto para casos de emergencia."""
        print("⚠️ Usando mapa por defecto.")
        # (Tu diccionario de mapa por defecto va aquí, no lo he cambiado)
        return {
            "width": 10, "height": 10, "goal": 1000,
            "tiles": [["C"]*10]*10,
            "legend": {"C": {"name": "calle"}, "B": {"name": "edificio", "blocked": True}}
        }


# Función de utilidad para obtener una instancia del proxy
def get_proxy() -> Proxy:
    """Retorna la instancia singleton del proxy."""
    return Proxy()

if __name__ == "__main__":
    # Esta sección solo se ejecuta cuando corres "python proxy.py" directamente
    # No se ejecutará cuando importes el Proxy desde main.py
    proxy = get_proxy()
    
    print("=== Testing Proxy ===")
    
    # Test map
    game_map = proxy.get_map()
    if game_map:
        print(f"Mapa cargado: {game_map.width}x{game_map.height}")
    
    # Test weather
    weather = proxy.get_weather()
    # (Nota: La clase Weather necesita un atributo 'state' para que esto funcione)
    # if weather:
    #     print(f"Clima inicial: {weather.state}")
    
    # Test orders
    orders = proxy.get_orders()
    if orders is not None:
        print(f"Pedidos cargados: {len(orders)}")
