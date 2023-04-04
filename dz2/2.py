import json
import random
import datetime


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', 'r', encoding='utf8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    data.setdefault('orders', []).append(order)
    with open('orders.json', 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    goods = ['Книга', 'Журнал', 'Газета', 'Учебник']
    clients = ['Иван', 'Петр', 'Алексей', 'Николай']
    write_order_to_json(
        random.choice(goods),
        random.randint(1, 20),
        "{:6.2f}".format(random.random() * 1000),
        random.choice(clients),
        str(datetime.date.today())
    )
