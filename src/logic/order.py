class Order:
    def __init__(self, id, pickup, dropoff, payout, deadline, weight, priority, release_time):
        self.id = id
        self.pickup = pickup
        self.dropoff = dropoff
        self.payout = payout
        self.deadline = deadline
        self.weight = weight
        self.priority = priority
        self.release_time = release_time

    def __repr__(self):
        return f"Pedido({self.id} - Prio: {self.priority})"

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia de Order desde un diccionario."""
        return cls(
            id=data.get('id'),
            pickup=data.get('pickup'),
            dropoff=data.get('dropoff'),
            payout=data.get('payout'),
            deadline=data.get('deadline'),
            weight=data.get('weight'),
            priority=data.get('priority'),
            release_time=data.get('release_time')
        )