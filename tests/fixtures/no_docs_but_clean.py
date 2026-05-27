def calculate_discount(price, percentage):
    return price * (percentage / 100)


def apply_tax(subtotal, tax_rate):
    tax = subtotal * tax_rate
    return subtotal + tax


def format_currency(amount):
    return f"${amount:.2f}"


def generate_invoice_line(item_name, quantity, unit_price):
    line_total = quantity * unit_price
    return {
        "item": item_name,
        "quantity": quantity,
        "unit_price": unit_price,
        "total": line_total,
    }
