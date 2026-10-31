from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from catalogo.models import Produto
from carrinho.cart import CART_SESSION_KEY, get_cart, get_cart_items

from .forms import FinalizacaoPedidoForm
from .models import ItemPedido, Pedido


@require_http_methods(['GET', 'POST'])
def finalizar_pedido(request):
    cart = get_cart(request.session)
    if not cart:
        messages.error(request, 'Adicione produtos ao carrinho antes de finalizar.')
        return redirect('carrinho:detalhe')

    itens, total = get_cart_items(request.session)
    form = FinalizacaoPedidoForm(request.POST or None)
    if request.method == 'GET':
        return render(request, 'pedidos/finalizar.html', {
            'form': form,
            'itens': itens,
            'total': total,
        })

    if not form.is_valid():
        return render(request, 'pedidos/finalizar.html', {
            'form': form,
            'itens': itens,
            'total': total,
        })

    try:
        if any(
            not str(product_id).isdigit()
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity < 1
            for product_id, quantity in cart.items()
        ):
            raise ValueError
        quantities = {int(product_id): quantity for product_id, quantity in cart.items()}
        if len(quantities) != len(cart):
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, 'O carrinho contém itens inválidos. Revise os produtos.')
        return redirect('carrinho:detalhe')

    with transaction.atomic():
        produtos = list(
            Produto.objects.select_for_update()
            .filter(pk__in=quantities, ativo=True)
            .order_by('pk')
        )
        produtos_por_id = {produto.pk: produto for produto in produtos}
        if len(produtos_por_id) != len(quantities):
            messages.error(
                request,
                'Um ou mais produtos não estão mais disponíveis. Revise o carrinho.',
            )
            return redirect('carrinho:detalhe')
        if any(produto.estoque < quantities[produto.pk] for produto in produtos):
            messages.error(
                request,
                'Estoque insuficiente para um ou mais produtos. Revise o carrinho.',
            )
            return redirect('carrinho:detalhe')

        total_pedido = sum(
            (produto.preco * quantities[produto.pk] for produto in produtos),
            start=0,
        )
        pedido = Pedido.objects.create(
            nome_cliente=form.cleaned_data['nome_cliente'],
            email_cliente=form.cleaned_data['email_cliente'],
            endereco_entrega=form.cleaned_data['endereco_entrega'],
            total=total_pedido,
        )
        for produto in produtos:
            quantidade = quantities[produto.pk]
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                nome_produto=produto.nome,
                preco_unitario=produto.preco,
                quantidade=quantidade,
            )
            produto.estoque -= quantidade
            produto.save(update_fields=['estoque'])

    request.session.pop(CART_SESSION_KEY, None)
    request.session.modified = True
    return render(request, 'pedidos/confirmacao.html', {'pedido': pedido})
