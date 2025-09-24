import requests
import json
import os
import pickle
from sys import path
path.append('..\\Courier_Quest-1')

from datetime import datetime, timedelta
from src.config.config import URL, CACHE_DIR, DATA_DIR, SAVES_DIR


# --- FUNCIONES DE API Y CACHÉ ---

def _get_cache_path(endpoint):
    """Genera la ruta del archivo de caché para un endpoint."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{endpoint.replace('/', '_')}.json")

def _load_from_api(endpoint):
    """Intenta cargar datos desde el API."""
    try:
        url = f"{URL}/{endpoint}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Guardar en caché
        cache_path = _get_cache_path(endpoint)
        with open(cache_path, 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': data}, f)
        print(f"Datos de '{endpoint}' cargados desde el API y cacheados.")
        return data
    except requests.RequestException as e:
        print(f"Error al conectar con el API en '{endpoint}': {e}")
        return None

def _load_from_cache(endpoint):
    """Intenta cargar datos desde la caché si no tiene más de 24 horas."""
    cache_path = _get_cache_path(endpoint)
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
        timestamp = datetime.fromisoformat(cached_data['timestamp'])
        if datetime.now() - timestamp < timedelta(hours=24):
            print(f"Datos de '{endpoint}' cargados desde la caché.")
            return cached_data['data']
    return None
    
def _load_from_local_file(filename):
    """Carga datos desde un archivo JSON local como último recurso."""
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            print(f"Cargando datos desde el archivo local de respaldo '{filename}'.")
            return json.load(f)
    print(f"¡ADVERTENCIA! No se pudo encontrar el archivo local '{filename}'.")
    return None

def get_game_data(endpoint, local_filename):
    """
    Obtiene los datos del juego siguiendo el orden: API -> Caché -> Archivo Local.
    """
    # 1. Intentar desde el API
    data = _load_from_api(endpoint)
    if data is not None:
        return data
        
    # 2. Si falla el API, intentar desde la caché
    data = _load_from_cache(endpoint)
    if data is not None:
        return data

    # 3. Como último recurso, cargar desde el archivo local
    return _load_from_local_file(local_filename)

# --- FUNCIONES DE PERSISTENCIA ---

def save_highscore(scores):
    """Guarda la lista de puntajes en un archivo JSON, ordenada."""
    scores.sort(key=lambda x: x['score'], reverse=True)
    path = os.path.join(DATA_DIR, 'puntajes.json')
    with open(path, 'w') as f:
        json.dump(scores, f, indent=4)

def load_highscore():
    """Carga la lista de puntajes desde el archivo JSON."""
    path = os.path.join(DATA_DIR, 'puntajes.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)

def save_game_state(state, slot=1):
    """Guarda el estado del juego en un archivo binario."""
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)
    path = os.path.join(SAVES_DIR, f'slot{slot}.sav')
    with open(path, 'wb') as f:
        pickle.dump(state, f)
    print(f"Partida guardada en la ranura {slot}.")

def load_game_state(slot=1):
    """Carga el estado del juego desde un archivo binario."""
    path = os.path.join(SAVES_DIR, f'slot{slot}.sav')
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        print(f"Cargando partida desde la ranura {slot}.")
        return pickle.load(f)



