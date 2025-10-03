import pytest
from datetime import datetime, timedelta
from src.logic.player import Player
from src.logic.order import Order


@pytest.fixture
def player():
    return Player(x=5, y=5, income_goal=1000)


@pytest.fixture
def sample_order():
    return Order(
        "PED-001",
        [3, 3],
        [10, 10],
        150,
        (datetime.now() + timedelta(minutes=5)).isoformat(),
        2,
        0,
        0
    )


def test_player_initialization(player):
    assert player.x == 5
    assert player.y == 5
    assert player.stamina == 100
    assert player.reputation == 70
    assert player.total_income == 0
    assert not player.is_exhausted


def test_accept_order(player, sample_order):
    result = player.accept_order(sample_order)
    assert result is True
    assert player.inventory.order_count == 1
    assert player.get_total_weight() == 2


def test_accept_order_exceeds_weight(player):
    heavy_orders = [
        Order(f"PED-{i}", [1, 1], [2, 2], 100, 
              datetime.now().isoformat(), 3, 0, 0)
        for i in range(5)
    ]
    
    for i in range(3):
        assert player.accept_order(heavy_orders[i]) is True
    
    # Cuarto pedido excede peso máximo (9 + 3 > 10)
    assert player.accept_order(heavy_orders[3]) is False


def test_stamina_consumption(player):
    initial_stamina = player.stamina
    
    player.consume_stamina("clear")
    
    assert player.stamina < initial_stamina
    assert player.stamina == 99.5  # -0.5 base


def test_stamina_consumption_weather(player):
    player.consume_stamina("storm")
    assert player.stamina == 99.2  # -0.5 - 0.3


def test_stamina_recovery(player):
    player.stamina = 50
    player.recover_stamina()
    assert player.stamina == 55
    
    player.recover_stamina(in_rest_point=True)
    assert player.stamina == 65


def test_exhaustion(player):
    player.stamina = 0
    player.consume_stamina("clear")
    
    assert player.is_exhausted is True
    assert player.move(1, 0, "clear", 1.0) is False


def test_recovery_from_exhaustion(player):
    player.stamina = 0
    player.is_exhausted = True
    
    for _ in range(6):
        player.recover_stamina()
    
    assert player.stamina == 30
    assert player.is_exhausted is False


def test_calculate_speed(player):
    speed = player.calculate_speed("clear", 1.0)
    assert speed == 3.0  # base speed
    
    speed = player.calculate_speed("storm", 1.0)
    assert speed == 2.25  # 3 * 0.75


def test_reputation_high_bonus(player):
    player.reputation = 90
    speed = player.calculate_speed("clear", 1.0)
    assert speed == pytest.approx(3.09)  # 3 * 1.03


def test_complete_delivery_on_time(player, sample_order):
    player.accept_order(sample_order)
    
    result = player.complete_delivery(datetime.now())
    
    assert result is not None
    assert result['rep_change'] > 0
    assert player.total_income > 0


def test_complete_delivery_late(player):
    late_order = Order(
        "PED-LATE",
        [1, 1],
        [2, 2],
        100,
        (datetime.now() - timedelta(minutes=3)).isoformat(),
        1,
        0,
        0
    )
    
    player.accept_order(late_order)
    result = player.complete_delivery(datetime.now())
    
    assert result['rep_change'] < 0


def test_cancel_order(player, sample_order):
    player.accept_order(sample_order)
    initial_rep = player.reputation
    
    player.cancel_order()
    
    assert player.reputation == initial_rep - 4
    assert player.inventory.order_count == 0


def test_defeat_condition(player):
    player.reputation = 15
    assert player.is_defeated() is True


def test_victory_condition(player):
    player.total_income = 1000
    assert player.has_won() is True


def test_delivery_streak_bonus(player):
    """Test que la racha de 3 entregas da bonus."""
    orders = [
        Order(f"PED-{i}", [1, 1], [2, 2], 100,
              (datetime.now() + timedelta(minutes=10)).isoformat(), 1, 0, 0)
        for i in range(3)
    ]
    
    initial_rep = player.reputation
    
    for order in orders:
        player.accept_order(order)
        player.complete_delivery(datetime.now())
    
    # +3 por cada entrega a tiempo + 2 de bonus por racha
    expected_rep = initial_rep + (3 * 3) + 2
    assert player.reputation == expected_rep