from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Order:
    id: str
    mine: str
    destination: str
    tons: int
    deadline_hour: int
    priority: int  # 1(low) - 5(high)


@dataclass(frozen=True)
class Truck:
    id: str
    location: str
    capacity_tons: int
    available_hour: int


@dataclass(frozen=True)
class Dispatch:
    order_id: str
    truck_id: str
    assigned_tons: int
    pickup_hour: int
    eta_hour: int
    delivery_score: float


TRAVEL_HOURS = {
    ("Mine-A", "Plant-1"): 3,
    ("Mine-A", "Plant-2"): 5,
    ("Mine-B", "Plant-1"): 4,
    ("Mine-B", "Plant-2"): 2,
}

TRUCK_REPOSITION_HOURS = {
    ("Yard-East", "Mine-A"): 1,
    ("Yard-East", "Mine-B"): 2,
    ("Yard-West", "Mine-A"): 2,
    ("Yard-West", "Mine-B"): 1,
    ("Mine-A", "Mine-A"): 0,
    ("Mine-B", "Mine-B"): 0,
    ("Mine-A", "Mine-B"): 2,
    ("Mine-B", "Mine-A"): 2,
}


def _trip_time(mine: str, destination: str) -> int:
    return TRAVEL_HOURS[(mine, destination)]


def _to_mine_time(location: str, mine: str) -> int:
    return TRUCK_REPOSITION_HOURS[(location, mine)]


def delivery_priority_score(order: Order, eta_hour: int) -> float:
    """
    Higher is better. Late delivery receives a significant penalty.
    Core objective: protect high-priority deliveries first.
    """
    lateness = max(0, eta_hour - order.deadline_hour)
    # Priority dominates; lateness strongly penalized.
    return order.priority * 100 - lateness * 30 - order.tons * 0.1


def dispatch_orders(orders: List[Order], trucks: List[Truck]) -> List[Dispatch]:
    remaining = {o.id: o.tons for o in orders}
    mutable_trucks = {t.id: {"location": t.location, "available_hour": t.available_hour} for t in trucks}

    # Iterate through candidate assignments by business value (priority desc + deadline asc).
    sorted_orders = sorted(orders, key=lambda o: (-o.priority, o.deadline_hour))
    plans: List[Dispatch] = []

    for order in sorted_orders:
        while remaining[order.id] > 0:
            best_candidate = None

            for t in trucks:
                state = mutable_trucks[t.id]
                pickup_hour = state["available_hour"] + _to_mine_time(state["location"], order.mine)
                eta_hour = pickup_hour + _trip_time(order.mine, order.destination)
                score = delivery_priority_score(order, eta_hour)

                if best_candidate is None or score > best_candidate["score"]:
                    assign_tons = min(t.capacity_tons, remaining[order.id])
                    best_candidate = {
                        "truck": t,
                        "pickup_hour": pickup_hour,
                        "eta_hour": eta_hour,
                        "score": score,
                        "assign_tons": assign_tons,
                    }

            if best_candidate is None:
                break

            truck = best_candidate["truck"]
            assign_tons = best_candidate["assign_tons"]
            remaining[order.id] -= assign_tons

            plans.append(
                Dispatch(
                    order_id=order.id,
                    truck_id=truck.id,
                    assigned_tons=assign_tons,
                    pickup_hour=best_candidate["pickup_hour"],
                    eta_hour=best_candidate["eta_hour"],
                    delivery_score=round(best_candidate["score"], 1),
                )
            )

            mutable_trucks[truck.id]["location"] = order.mine
            mutable_trucks[truck.id]["available_hour"] = best_candidate["eta_hour"]

    return plans


def print_plan(dispatches: List[Dispatch]) -> None:
    print("=== AI调度演示系统（煤炭 + 指派调度 + 保交付优先）===")
    print("order   truck   tons   pickup  eta  score")
    print("-" * 46)
    for d in dispatches:
        print(
            f"{d.order_id:<7} {d.truck_id:<7} {d.assigned_tons:<5} "
            f"{d.pickup_hour:<7} {d.eta_hour:<4} {d.delivery_score:<5}"
        )


def demo() -> List[Dispatch]:
    orders = [
        Order("O-101", "Mine-A", "Plant-1", tons=60, deadline_hour=10, priority=5),
        Order("O-102", "Mine-B", "Plant-2", tons=45, deadline_hour=9, priority=4),
        Order("O-103", "Mine-A", "Plant-2", tons=30, deadline_hour=12, priority=3),
    ]

    trucks = [
        Truck("T-01", "Yard-East", capacity_tons=30, available_hour=0),
        Truck("T-02", "Yard-West", capacity_tons=25, available_hour=0),
        Truck("T-03", "Mine-A", capacity_tons=20, available_hour=1),
    ]

    dispatches = dispatch_orders(orders, trucks)
    print_plan(dispatches)
    return dispatches


if __name__ == "__main__":
    demo()
