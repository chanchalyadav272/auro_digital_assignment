import xml.etree.ElementTree as ET
import heapq
from datetime import datetime
from collections import defaultdict, OrderedDict

# Order Representation
class OrderModel:
    def __init__(self, id, type, cost, quantity, time):
        self.id = id
        self.type = type
        self.cost = float(cost)
        self.quantity = int(quantity)
        self.time = time

    def __lt__(self, other_order):
        if self.type == 'BUY':
            return (self.cost, -self.time) > (other_order.cost, -other_order.time)
        return (self.cost, self.time) < (other_order.cost, other_order.time)

def print_order_books(order_books):
     for name, book in order_books.items():
        print(f"Book: {name}")
        print("      Buy -- Sell")
        print("========================")
        print(book)
        print()

# Order Book for Asset Management
class OrderBook:
    def __init__(self):
        self.buys = []
        self.sells = []
        self.orders = {}

    def add_order(self, order):
        self.execute_match(order)
        if order.quantity > 0:
            target = self.buys if order.type == 'BUY' else self.sells
            heapq.heappush(target, order)
            self.orders[order.id] = order

    def delete_order(self, id):
        if id in self.orders:
            self.orders[id].quantity = 0

    def execute_match(self, incoming_order):
        opposite = self.sells if incoming_order.type == 'BUY' else self.buys
        while opposite and incoming_order.quantity > 0:
            top = opposite[0]
            if top.quantity == 0:
                heapq.heappop(opposite)
                del self.orders[top.id]
                continue
            if (incoming_order.type == 'BUY' and incoming_order.cost >= top.cost) or (incoming_order.type == 'SELL' and incoming_order.cost <= top.cost):
                matched_quantity = min(incoming_order.quantity, top.quantity)
                incoming_order.quantity -= matched_quantity
                top.quantity -= matched_quantity
                if top.quantity == 0:
                    heapq.heappop(opposite)
                    del self.orders[top.id]
            else:
                break

    def __str__(self):
        valid_buys = [o for o in self.buys if o.quantity > 0]
        valid_sells = [o for o in self.sells if o.quantity > 0]
        valid_buys.sort()
        valid_sells.sort()
        max_len = max(len(valid_buys), len(valid_sells))
        order_display = []

        for i in range(max_len):
            buy_str = f"{valid_buys[i].quantity}@{valid_buys[i].cost:.2f}" if i < len(valid_buys) else " " * 8
            sell_str = f"{valid_sells[i].quantity}@{valid_sells[i].cost:.2f}" if i < len(valid_sells) else ""
            order_display.append(f"{buy_str} -- {sell_str}")

        return '\n'.join(order_display)

# XML Processing for Orders
def process_xml_orders(file_path):
    order_books = defaultdict(OrderBook)
    start = datetime.now()

    xml_tree = ET.parse(file_path)
    root_element = xml_tree.getroot()
    time_counter = 0
    for msg in root_element:
        book_key = msg.attrib['book']
        id = msg.attrib['orderId']
        time_counter += 1
        if msg.tag == 'AddOrder':
            operation_type = msg.get('ops')
            price = float(msg.get('price'))
            volume = int(msg.get('vol'))
            new_order = OrderModel(id, operation_type, price, volume, time_counter)
            order_books[book_key].add_order(new_order)
        elif msg.tag == 'DeleteOrder':
            order_books[book_key].delete_order(id)

    finish = datetime.now()
    elapsed = (finish - start).total_seconds()
    sorted_order_books = OrderedDict(sorted(order_books.items()))
    print(f"Processing started at: {start.strftime('%Y-%m-%d %H:%M:%S.%f')}\n")
    print_order_books(sorted_order_books)
    print(f"Processing completed at: {finish.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Processing Duration: {elapsed:.3f} seconds\n")
    return order_books

# Execution of the XML Processing
if __name__ == '__main__':
    xml_file = "orders.xml"
    process_xml_orders(xml_file)
