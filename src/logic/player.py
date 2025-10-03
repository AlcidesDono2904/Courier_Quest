from datetime import datetime
from src.config.config import (
    WEATHER_MULTIPLIERS, REP_BONUS_EARLY, REP_BONUS_ON_TIME,
    REP_PENALTY_SLIGHTLY_LATE, REP_PENALTY_LATE, REP_PENALTY_VERY_LATE,
    REP_BONUS_STREAK, REP_PENALTY_CANCEL_ORDER, ORDER_BASE_TIME_SECONDS,
    STAMINA_RECOVERY_AT_POINT, STAMINA_RECOVERY_RESTING, STAMINA_EXHAUSTED_THRESHOLD
)
from .inventory import Inventory


class Player:
    """Representa al repartidor (jugador)."""

    def __init__(self, x, y, income_goal):
        self.x = x
        self.y = y
        self.income_goal = income_goal

        self.inventory = Inventory(max_weight=10)
        self.stamina = 100
        self.reputation = 70
        self.total_income = 0
        self.is_exhausted = False

        self.base_speed = 3
        self.stamina_consumption_base = 0.5
        
        self.deliveries_streak = 0
        self.first_late_today = True
        self.total_penalties = 0

    def get_total_weight(self):
        """Calcula peso total del inventario."""
        return self.inventory.current_weight

    def get_weather_multiplier(self, weather_condition):
        """Obtiene multiplicador de clima."""
        return WEATHER_MULTIPLIERS.get(weather_condition, 1.0)

    def calculate_speed(self, weather_condition, surface_weight_tile):
        """Calcula velocidad actual del jugador."""
        total_weight = self.get_total_weight()
        m_weather = self.get_weather_multiplier(weather_condition)
        m_weight = max(0.8, 1 - 0.03 * total_weight)
        m_rep = 1.03 if self.reputation >= 90 else 1.0

        if self.stamina <= 0:
            m_stamina = 0.0
        elif self.stamina < STAMINA_EXHAUSTED_THRESHOLD:
            m_stamina = 0.8
        else:
            m_stamina = 1.0

        speed = (self.base_speed * m_weather * m_weight *
                m_rep * m_stamina * surface_weight_tile)
        return speed

    def consume_stamina(self, weather_condition):
        """Calcula y consume resistencia por movimiento."""
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
        
        self.stamina = max(0, self.stamina - consumption)

        if self.stamina <= 0:
            self.is_exhausted = True

    def recover_stamina(self, dt, in_rest_point=False):
        """Recupera resistencia."""
        recovery_rate = STAMINA_RECOVERY_AT_POINT if in_rest_point else STAMINA_RECOVERY_RESTING
        self.stamina = min(100, self.stamina + recovery_rate * dt)

        if self.stamina >= STAMINA_EXHAUSTED_THRESHOLD and self.is_exhausted:
            self.is_exhausted = False

    def can_move(self):
        """Verifica si el jugador puede moverse (no exhausto)."""
        return not self.is_exhausted and self.stamina > 0

    def accept_order(self, order):
        """Acepta un pedido y lo añade al inventario."""
        try:
            self.inventory.add_order(order)
            return True
        except ValueError as e:
            print(f"No se puede aceptar: {e}")
            return False

    def complete_delivery(self, current_time):
        """Completa entrega actual y actualiza reputación/ingresos."""
        if self.inventory.current_order is None:
            return None

        order = self.inventory.current_order.order
        deadline = datetime.fromisoformat(order.deadline)
        time_diff = (deadline - current_time).total_seconds()

        rep_change = 0
        if time_diff >= 0:
            if time_diff >= 0.20 * ORDER_BASE_TIME_SECONDS:
                rep_change = REP_BONUS_EARLY
            else:
                rep_change = REP_BONUS_ON_TIME
            self.deliveries_streak += 1
        else:
            time_late = abs(time_diff)
            if time_late <= 30:
                rep_change = REP_PENALTY_SLIGHTLY_LATE
            elif time_late <= 120:
                rep_change = REP_PENALTY_LATE
            else:
                rep_change = REP_PENALTY_VERY_LATE

            if self.first_late_today and self.reputation >= 85:
                rep_change //= 2
                self.first_late_today = False

            self.deliveries_streak = 0

        if self.deliveries_streak >= 3:
            rep_change += REP_BONUS_STREAK
            self.deliveries_streak = 0

        self.reputation = max(0, min(100, self.reputation + rep_change))

        payout = order.payout
        if self.reputation >= 90:
            payout *= 1.05

        self.total_income += payout

        completed = self.inventory.complete_current_order()

        return {
            'order': completed,
            'payout': payout,
            'rep_change': rep_change
        }

    def cancel_order(self):
        """Cancela pedido actual."""
        if self.inventory.current_order:
            self.reputation = max(0, self.reputation - REP_PENALTY_CANCEL_ORDER)
            
            payout_lost = self.inventory.current_order.order.payout * 0.25
            self.total_penalties += int(payout_lost)

            self.inventory.complete_current_order()
            self.deliveries_streak = 0
            
            print(f"Pedido cancelado. Penalización de reputación y ${int(payout_lost)} al puntaje.")
            return True
        return False

    def expire_order(self, order_to_expire):
        """Maneja la lógica para un pedido expirado."""
        print(f"¡El pedido {order_to_expire.id} ha expirado!")
        
        self.reputation = max(0, self.reputation - 6)
        
        payout_lost = order_to_expire.payout * 0.30
        self.total_penalties += int(payout_lost)
        
        self.deliveries_streak = 0
        
        self.inventory.remove_order_by_id(order_to_expire.id)

    def is_defeated(self):
        """Verifica si el jugador ha perdido."""
        return self.reputation < 20

    def has_won(self):
        """Verifica si el jugador ha ganado."""
        return self.total_income >= self.income_goal