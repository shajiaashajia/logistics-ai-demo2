from scheduler_demo import Order, Truck, dispatch_orders


def test_high_priority_order_dispatched_first():
    orders = [
        Order("LOW", "Mine-A", "Plant-2", tons=20, deadline_hour=20, priority=1),
        Order("HIGH", "Mine-A", "Plant-1", tons=20, deadline_hour=8, priority=5),
    ]
    trucks = [Truck("T-1", "Mine-A", capacity_tons=20, available_hour=0)]

    plan = dispatch_orders(orders, trucks)

    assert plan[0].order_id == "HIGH"


def test_all_orders_fully_assigned_when_capacity_available():
    orders = [
        Order("A", "Mine-B", "Plant-2", tons=20, deadline_hour=10, priority=4),
        Order("B", "Mine-A", "Plant-1", tons=20, deadline_hour=10, priority=4),
    ]
    trucks = [
        Truck("T-1", "Mine-B", capacity_tons=20, available_hour=0),
        Truck("T-2", "Mine-A", capacity_tons=20, available_hour=0),
    ]

    plan = dispatch_orders(orders, trucks)

    assigned = {}
    for p in plan:
        assigned[p.order_id] = assigned.get(p.order_id, 0) + p.assigned_tons

    assert assigned == {"A": 20, "B": 20}
