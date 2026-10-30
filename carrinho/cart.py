from decimal import Decimal

from catalogo.models import Produto


CART_SESSION_KEY = 'carrinho'


def get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def add_product(session, product_id):
    cart = get_cart(session)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session[CART_SESSION_KEY] = cart
    session.modified = True


def get_cart_items(session):
    cart = get_cart(session)
    products = Produto.objects.filter(pk__in=cart.keys()).select_related('categoria')
    products_by_id = {str(product.pk): product for product in products}
    items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = products_by_id.get(str(product_id))
        if product is None:
            continue
        subtotal = product.preco * quantity
        total += subtotal
        items.append({
            'produto': product,
            'quantidade': quantity,
            'subtotal': subtotal,
        })
    return items, total
