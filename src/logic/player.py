import pygame
from datetime import datetime
import src.config.config as config
from .inventory import Inventory
from .order import Order

class Player:
    def __init__(self, x, y, income_goal):
        
        self.x = x #poscion del jugador 
        self.y = y #poscion del jugador
        self.income_goal = income_goal
        
        self.max_weight = 30
        self.inventory = Inventory(peso_maximo=self.max_weight)
        self.stamina = 100
        self.reputation = 70
        
        self.total_income = 0
        self.is_exhausted = False
        
        # Atributos para Pygame
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        # Variables para los cálculos de velocidad y resistencia
        self.base_speed = 3
        self.stamina_consumption_base = 0.5
        self.last_position = (x, y) 

    def get_total_weight(self) -> int:
        
        return self.inventory.current_weight

    def get_weather_multiplier(self, weather_condition: str) -> float:
        
      return config.WEATHER_MULTIPLIERS.get(weather_condition, 1.0)
        
    def calculate_speed(self, weather_condition: str, surface_weight_tile: float) -> float:
        
        total_weight = self.get_total_weight()
        m_weather = self.get_weather_multiplier(weather_condition)
        m_weight = max(0.8, 1 - 0.03 * total_weight)
        m_rep = 1.03 if self.reputation >= 90 else 1.0
        
        if self.stamina < 30 and self.stamina > 0:
            m_stamina = 0.8
        elif self.stamina <= 0:
            m_stamina = 0.0
        else:
            m_stamina = 1.0

        speed = self.base_speed * m_weather * m_weight * m_rep * m_stamina * surface_weight_tile
        return speed

    def consume_stamina(self, weather_condition: str):
        
        total_weight = self.get_total_weight()
        consumption = self.stamina_consumption_base
        
        if total_weight > 3:
            consumption += 0.2 * (total_weight - 3)
        
        if weather_condition in ["rain", "wind"]:
            consumption += 0.1
        elif weather_condition == "storm":
            consumption += 0.3
        elif weather_condition == "heat":
            consumption += 0.2
        
        self.stamina -= consumption
        
        if self.stamina <= 0:
            self.is_exhausted = True
            print("El jugador está exhausto y no puede moverse.")
            
    def recover_stamina(self):
        
        self.stamina += 5
        
        if self.stamina > 100:
            self.stamina = 100
        
        if self.stamina >= 30 and self.is_exhausted:
            self.is_exhausted = False
            print("El jugador se ha recuperado y puede moverse de nuevo.")
    
    def move(self, dx, dy, weather_condition, surface_weight_tile):
        
        if not self.is_exhausted:
            self.x += dx
            self.y += dy
            self.consume_stamina(weather_condition)
        else:
            print("El jugador está agotado. Debe descansar para recuperarse.")
            
    def accept_delivery(self, delivery: Order) -> bool:
       
        try:
            return self.inventory.add_order(delivery)
        except ValueError as e:
            print(f"No se puede aceptar el pedido: {e}")
            return False
        
    def dropoff_delivery(self, current_time: datetime):
        
        delivery = self.inventory.complete_current_order()
        if not delivery:
            print("No hay pedido para entregar.")
            return

        deadline = delivery.deadline

        time_difference = (deadline - current_time).total_seconds()

        reputation_change = 0
        if time_difference >= 0:
            if time_difference > 0.20 * (deadline - datetime.fromisoformat(delivery.release_time)).total_seconds():
                reputation_change = 5
            else:
                reputation_change = 3
        else:
            time_late = abs(time_difference)
            if time_late <= 30:
                reputation_change = -2
            elif time_late <= 120:
                reputation_change = -5
            else:
                reputation_change = -10

        self.reputation += reputation_change
        if self.reputation < 20:
            print("Reputación por debajo de 20. ¡Has perdido!")
        
        payout = delivery.payout
        if self.reputation >= 90:
            payout *= 1.05
            
        self.total_income += payout
        
        print(f"Pedido {delivery.id} entregado. Ganancias: {payout}. Nueva reputación: {self.reputation}.")

    def update_state(self):
        if (self.x, self.y) == self.last_position:
            self.recover_stamina()
        else:
            self.last_position = (self.x, self.y)
        pass

    def draw(self, screen):
        self.rect.topleft = (self.x, self.y)
        screen.blit(self.image, self.rect)