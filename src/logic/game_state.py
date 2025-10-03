import pickle
import json
from datetime import datetime
from pathlib import Path


class GameState:
    """Maneja guardado, carga y sistema de deshacer."""
    
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
    
    def save_game(self, slot, player, inventory, game_data):
        """Guarda partida en archivo binario."""
        data = {
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
    
    def load_game(self, slot):
        """Carga partida desde archivo binario."""
        try:
            with open(f"saves/slot{slot}.sav", 'rb') as f:
                data = pickle.load(f)
            print(f"Juego cargado desde slot {slot}")
            return data
        except FileNotFoundError:
            print(f"No existe guardado en slot {slot}")
            return None
    
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
        """Guarda puntaje en JSON ordenado."""
        try:
            with open("data/puntajes.json", 'r') as f:
                scores = json.load(f)
        except FileNotFoundError:
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
        scores = scores[:10]  # Top 10
        
        with open("data/puntajes.json", 'w') as f:
            json.dump(scores, f, indent=2)
        
        return scores