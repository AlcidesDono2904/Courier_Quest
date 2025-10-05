from .order import Order

class Node:
    def __init__(self, order: Order):
        self.order = order
        self.next = None
        self.prev = None


class Inventory:
    def __init__(self, max_weight=10):
        self.first = None
        self.last = None
        self.current_order = None
        self.max_weight = max_weight
        self.current_weight = 0
        self.order_count = 0

    def add_order(self, order: Order):
        if self.current_weight + order.weight > self.max_weight:
            raise ValueError(f"Cannot add {order.id}. Exceeds maximum weight.")

        new_node = Node(order)
        if self.first is None:
            self.first = new_node
            self.last = new_node
            self.current_order = new_node
        else:
            self.last.next = new_node
            new_node.prev = self.last
            self.last = new_node

        self.current_weight += order.weight
        self.order_count += 1
        print(f"Order {order.id} added to inventory.")
        return True

    def view_next_order(self):
        if self.current_order and self.current_order.next:
            self.current_order = self.current_order.next
            print(f"Viewing order: {self.current_order.order.id}")
        else:
            print("Already at the last order.")

    def view_prev_order(self):
        if self.current_order and self.current_order.prev:
            self.current_order = self.current_order.prev
            print(f"Viewing order: {self.current_order.order.id}")
        else:
            print("Already at the first order.")

    def complete_current_order(self):
        if self.current_order is None:
            print("No order selected to complete.")
            return

        completed_order = self.current_order.order

        if self.current_order.prev:
            self.current_order.prev.next = self.current_order.next
        else:
            self.first = self.current_order.next

        if self.current_order.next:
            self.current_order.next.prev = self.current_order.prev
        else:
            self.last = self.current_order.prev

        # Avanza al siguiente pedido si existe, sino al anterior
        if self.current_order.next:
            self.current_order = self.current_order.next
        else:
            self.current_order = self.current_order.prev

        self.current_weight -= completed_order.weight
        self.order_count -= 1
        print(f"Order {completed_order.id} completed!")
        return completed_order

    def sort_inventory(self, key):
        """
        Ordena el inventario in-place en orden DESCENDENTE según la función key.
        Usa algoritmo de ordenamiento por inserción optimizado.
        
        Args:
            key (callable): Función que toma un Order y retorna un valor comparable
        """
        if not self.first or not self.first.next:
            print("Inventory has less than 2 items, no sorting needed.")
            return

        current_id = self.current_order.order.id if self.current_order else None

        nodes_list = []
        current = self.first
        while current:
            nodes_list.append(current)
            current = current.next

        nodes_list.sort(key=lambda node: key(node.order), reverse=True)

        for i, node in enumerate(nodes_list):
            if i == 0:
                self.first = node
                node.prev = None
            else:
                node.prev = nodes_list[i - 1]
                nodes_list[i - 1].next = node
            
            if i == len(nodes_list) - 1:
                self.last = node
                node.next = None

        if current_id is not None:
            node = self.first
            while node:
                if node.order.id == current_id:
                    self.current_order = node
                    break
                node = node.next
        else:
            self.current_order = self.first

        print("Inventory sorted successfully.")

    def remove_order_by_id(self, order_id):
        """Elimina un pedido del inventario por su ID."""
        node_to_remove = None
        current = self.first
        while current:
            if current.order.id == order_id:
                node_to_remove = current
                break
            current = current.next

        if node_to_remove is None:
            return False

        # Si el pedido a eliminar es el actual, mover el puntero `current_order`
        if node_to_remove == self.current_order:
            if self.current_order.next:
                self.current_order = self.current_order.next
            else:
                self.current_order = self.current_order.prev

        # Desconectar el nodo de la lista
        if node_to_remove.prev:
            node_to_remove.prev.next = node_to_remove.next
        else:
            self.first = node_to_remove.next

        if node_to_remove.next:
            node_to_remove.next.prev = node_to_remove.prev
        else:
            self.last = node_to_remove.prev

        self.current_weight -= node_to_remove.order.weight
        self.order_count -= 1
        print(f"Order {order_id} removed from inventory.")
        return True