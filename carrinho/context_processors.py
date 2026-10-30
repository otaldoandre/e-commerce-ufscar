from .cart import get_cart


def carrinho(request):
    quantidade = sum(get_cart(request.session).values())
    return {'carrinho_quantidade': quantidade}
