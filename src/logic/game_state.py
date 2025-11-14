import pickle
import json
from datetime import datetime
from pathlib import Path

class GameState:
    """Maneja guardado, carga, sistema de deshacer y utilidades de slots."""
    
    MAX_SLOTS = 3

    def __init__(self, max_undo=10):
        self.history = []
        self.max_undo = max_undo
        Path("saves").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
    
    def save_state(self, player, inventory, current_time, weather_state):
        """Guarda estado para deshacer."""
        state = {
            'player_pos': (player.x, player.y),
            'stamina': player.stamina,
            'reputation': player.reputation,
            'income': player.total_income,
            'inventory': self._serialize_inventory(inventory),
            'time': current_time,
            'weather': weather_state
        }
        self.history.append(state)
        if len(self.history) > self.max_undo:
            self.history.pop(0)
    
    def undo(self, steps=1):
        """Deshace N pasos."""
        if len(self.history) < steps + 1:
            return None
        for _ in range(steps):
            self.history.pop()
        return self.history[-1] if self.history else None

    def save_game(self, slot, player, inventory, game_data, player_name):
        """Guarda partida en slot específico (1..MAX_SLOTS)."""
        slot = int(slot)
        assert 1 <= slot <= self.MAX_SLOTS, f"Slot inválido: {slot}"
        data = {
            'player_name': player_name,
            'player': {
                'x': player.x,
                'y': player.y,
                'stamina': player.stamina,
                'reputation': player.reputation,
                'total_income': player.total_income,
                'income_goal': player.income_goal
            },
            'inventory': self._serialize_inventory(inventory),
            'game_data': game_data,
            'timestamp': datetime.now().isoformat()
        }
        with open(f"saves/slot{slot}.sav", 'wb') as f:
            pickle.dump(data, f)
        print(f"Juego guardado en slot {slot}")
        return True

    def auto_save(self, player, inventory, game_data, player_name):
        """
        Guarda usando F5: elige automáticamente:
        - Primer slot vacío (1..3), o
        - Si están llenos, sobrescribe el MÁS ANTIGUO.
        Devuelve el número de slot usado.
        """
        meta = self.list_slots_metadata()
       
        for i in range(1, self.MAX_SLOTS + 1):
            if not meta[i]['exists']:
                self.save_game(i, player, inventory, game_data, player_name)
                return i
       
        oldest_slot = min(
            (i for i in range(1, self.MAX_SLOTS + 1)),
            key=lambda i: meta[i]['mtime'] or datetime.max
        )
        self.save_game(oldest_slot, player, inventory, game_data, player_name)
        return oldest_slot
    
    def load_game(self, slot):
        """Carga partida desde archivo binario (dict) o None si no existe."""
        try:
            with open(f"saves/slot{slot}.sav", 'rb') as f:
                data = pickle.load(f)
            print(f"Juego cargado desde slot {slot}")
            return data
        except FileNotFoundError:
            print(f"No existe guardado en slot {slot}")
            return None

    def list_slots_metadata(self):
        """
        Devuelve dict {1:{exists, mtime, display_mtime, header}, 2:{...}, 3:{...}}
        header incluye un mini resumen: name, income, reputation, elapsed (si está).
        """
        info = {}
        for slot in range(1, self.MAX_SLOTS + 1):
            path = Path(f"saves/slot{slot}.sav")
            exists = path.exists()
            mtime = datetime.fromtimestamp(path.stat().st_mtime) if exists else None
            display_mtime = mtime.strftime("%Y-%m-%d %H:%M") if mtime else "—"
            header = None
            if exists:
                try:
                    with open(path, "rb") as f:
                        data = pickle.load(f)
                    player = data.get('player', {})
                    gd = data.get('game_data', {})
                    header = {
                        'name': data.get('player_name', 'Player'),
                        'income': player.get('total_income', 0),
                        'reputation': player.get('reputation', 0),
                        'elapsed': float(gd.get('elapsed_time', 0.0)),
                        'timestamp': data.get('timestamp', display_mtime),
                    }
                except Exception:
                    header = None
            info[slot] = {
                'exists': exists,
                'mtime': mtime,
                'display_mtime': display_mtime,
                'header': header
            }
        return info
    
    def _serialize_inventory(self, inventory):
        """Serializa inventario a lista."""
        orders = []
        node = inventory.first
        while node:
            orders.append({
                'id': node.order.id,
                'pickup': node.order.pickup,
                'dropoff': node.order.dropoff,
                'payout': node.order.payout,
                'deadline': node.order.deadline,
                'weight': node.order.weight,
                'priority': node.order.priority
            })
            node = node.next
        return orders
    
    @staticmethod
    def save_score(player_name, score, income, reputation):
        """Guarda puntaje en JSON ordenado (Top 10)."""
        try:
            with open("data/puntajes.json", 'r') as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = []
        
        new_score = {
            'name': player_name,
            'score': score,
            'income': income,
            'reputation': reputation,
            'date': datetime.now().isoformat()
        }
        
        scores.append(new_score)
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:10]
        
        with open("data/puntajes.json", 'w') as f:
            json.dump(scores, f, indent=2)
        
        return scores
    
    def delete_slot(self, slot) -> bool:
        """Elimina el archivo del slot indicado. Devuelve True si se borró."""
        path = Path(f"saves/slot{int(slot)}.sav")
        try:
            if path.exists():
                path.unlink()
                print(f"Slot {slot} eliminado.")
                return True
        except Exception as e:
            print(f"No se pudo eliminar el slot {slot}: {e}")
        return False