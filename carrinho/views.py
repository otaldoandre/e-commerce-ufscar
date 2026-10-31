from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalogo.models import Produto

from .cart import add_product, get_cart, get_cart_items


@require_POST
def adicionar_ao_carrinho(request, pk):
    produto = get_object_or_404(Produto, pk=pk, ativo=True)
    quantidade_atual = get_cart(request.session).get(str(produto.pk), 0)
    if produto.estoque < 1 or quantidade_atual >= produto.estoque:
        messages.error(request, f'{produto.nome} está esgotado.')
    else:
        add_product(request.session, produto.pk)
        messages.success(request, f'{produto.nome} foi adicionado ao carrinho.')
    destino = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        destino = 'catalogo:produto_lista'
    return redirect(destino)


@require_POST
def remover_do_carrinho(request, pk):
    cart = get_cart(request.session)
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['carrinho'] = cart
        request.session.modified = True
        messages.success(request, 'Produto removido do carrinho.')
    else:
        messages.error(request, 'Esse produto não está no carrinho.')
    return redirect('carrinho:detalhe')


def detalhe_carrinho(request):
    itens, total = get_cart_items(request.session)
    return render(request, 'carrinho/detalhe.html', {
        'itens': itens,
        'total': total,
    })
