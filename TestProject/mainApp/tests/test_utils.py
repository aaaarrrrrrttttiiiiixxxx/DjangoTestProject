def is_product_fields_equal(dict, product):
    return product.name == dict["name"] and product.category == dict["category"] and product.price == dict[
        "price"] and product.description == dict["description"] and product.url == dict["url"]


def is_basket_fields_equal(dict, basket):
    return basket.user == dict["user"] and basket.quantity == dict["quantity"] and basket.actual_price == dict[
        "actual_price"] and is_product_fields_equal(dict["product"], basket.product)


def is_basket_fields_ok(dict, user, product, quantity, actual_price):
    return user == dict["user"] and quantity == dict["quantity"] and actual_price == dict[
        "actual_price"] and dict["product_id"] == product.id


def is_order_items_response_fields_ok(dict, product, quantity, actual_price):
    return product.id == dict["product"] and quantity == dict["quantity"] and actual_price == dict["actual_price"]


def is_order_response_fields_ok(dict, user, delivery_id, address, payment_id, total_price, items):
    ok = True
    order_items = dict['order_items']
    for i, item in enumerate(order_items):
        ok = ok and is_order_items_response_fields_ok(item, items[i]['product'], items[i]['quantity'],
                                                      items[i]['actual_price'])
    return user == dict["user"] and delivery_id == dict["delivery_id"] and address == dict[
        "address"] and dict["payment_id"] == payment_id and dict["total_price"] == total_price and ok


def is_order_items_fields_ok(dict, product, quantity, actual_price):
    return product.id == dict["product_id"] and quantity == dict["quantity"] and actual_price == dict["actual_price"]


def is_order_fields_ok(order, order_items, user, delivery_id, address, payment_id, total_price, items):
    ok = True
    for i, item in enumerate(order_items):
        ok = ok and is_order_items_fields_ok(item, items[i]['product'], items[i]['quantity'], items[i]['actual_price'])
    return user == order.user and delivery_id == order.delivery_id and address == order.address and \
           order.payment_id == payment_id and order.total_price == total_price and ok