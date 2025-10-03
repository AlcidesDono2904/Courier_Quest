import pytest
from src.logic.inventory import Inventory
from src.logic.order import Order


@pytest.fixture
def sample_orders():
    return [
        Order("PED-001", [1, 1], [5, 5], 100, "2025-09-29T12:00:00", 2, 0, 0),
        Order("PED-002", [2, 2], [6, 6], 200, "2025-09-29T12:30:00", 3, 2, 0),
        Order("PED-003", [3, 3], [7, 7], 150, "2025-09-29T12:15:00", 1, 1, 0),
    ]


def test_inventory_creation():
    inv = Inventory(max_weight=10)
    assert inv.max_weight == 10
    assert inv.current_weight == 0
    assert inv.order_count == 0
    assert inv.first is None


def test_add_order(sample_orders):
    inv = Inventory(max_weight=10)
    
    result = inv.add_order(sample_orders[0])
    assert result is True
    assert inv.current_weight == 2
    assert inv.order_count == 1
    assert inv.first.order.id == "PED-001"


def test_add_order_exceeds_weight(sample_orders):
    inv = Inventory(max_weight=5)
    
    inv.add_order(sample_orders[0])  # peso 2
    
    with pytest.raises(ValueError):
        inv.add_order(sample_orders[1])  # peso 3, total = 5 OK pero luego falla con otro


def test_navigation(sample_orders):
    inv = Inventory(max_weight=10)
    
    for order in sample_orders:
        inv.add_order(order)
    
    assert inv.current_order.order.id == "PED-001"
    
    inv.view_next_order()
    assert inv.current_order.order.id == "PED-002"
    
    inv.view_prev_order()
    assert inv.current_order.order.id == "PED-001"


def test_complete_order(sample_orders):
    inv = Inventory(max_weight=10)
    
    inv.add_order(sample_orders[0])
    inv.add_order(sample_orders[1])
    
    completed = inv.complete_current_order()
    
    assert completed.id == "PED-001"
    assert inv.order_count == 1
    assert inv.current_weight == 3


def test_sort_by_priority(sample_orders):
    inv = Inventory(max_weight=10)
    
    for order in sample_orders:
        inv.add_order(order)
    
    inv.sort_inventory(key=lambda o: o.priority)
    
    # Orden descendente por prioridad: PED-002(2), PED-003(1), PED-001(0)
    assert inv.first.order.id == "PED-002"
    assert inv.first.next.order.id == "PED-003"
    assert inv.last.order.id == "PED-001"


def test_sort_by_weight(sample_orders):
    inv = Inventory(max_weight=10)
    
    for order in sample_orders:
        inv.add_order(order)
    
    inv.sort_inventory(key=lambda o: o.weight)
    
    # Orden descendente por peso: PED-002(3), PED-001(2), PED-003(1)
    assert inv.first.order.id == "PED-002"
    assert inv.last.order.id == "PED-003"