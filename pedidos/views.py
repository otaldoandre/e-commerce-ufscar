from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from catalogo.models import Produto
from carrinho.cart import CART_SESSION_KEY, get_cart, get_cart_items
from clientes.models import Cliente

from .forms import AcompanhamentoPedidoForm, FinalizacaoPedidoForm
from .models import ItemPedido, Pedido
from .pagamentos import autorizar_pagamento


@login_required(login_url='clientes:login')
@require_http_methods(['GET', 'POST'])
def finalizar_pedido(request):
    cliente = getattr(request.user, 'cliente', None)
    if cliente is None:
        messages.error(
            request,
            'Complete seu cadastro antes de finalizar a compra.',
        )
        return redirect('clientes:cadastro')

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
        cliente = Cliente.objects.select_for_update().get(pk=cliente.pk)
        pontos_resgatados = 0
        if cliente is not None and cliente.pontos_fidelidade >= 100:
            total_pedido = max(total_pedido - Decimal('10.00'), Decimal('0.00'))
            pontos_resgatados = 100
        resultado_pagamento = autorizar_pagamento(
            form.cleaned_data['forma_pagamento'],
            total_pedido,
        )
        if not resultado_pagamento.autorizado:
            form.add_error(None, resultado_pagamento.mensagem)
            return render(request, 'pedidos/finalizar.html', {
                'form': form,
                'itens': itens,
                'total': total,
            })

        pedido = Pedido.objects.create(
            nome_cliente=cliente.nome,
            email_cliente=cliente.email,
            endereco_entrega=cliente.endereco,
            total=total_pedido,
            status=Pedido.Status.CONFIRMADO,
            forma_pagamento=form.cleaned_data['forma_pagamento'],
            status_pagamento=Pedido.StatusPagamento.AUTORIZADO,
            cliente=cliente,
        )
        cliente.pontos_fidelidade = (
            cliente.pontos_fidelidade
            - pontos_resgatados
            + int(total_pedido)
        )
        cliente.save(update_fields=['pontos_fidelidade', 'atualizado_em'])
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


@require_http_methods(['GET', 'POST'])
@login_required(login_url='clientes:login')
def acompanhar_pedido(request):
    cliente = getattr(request.user, 'cliente', None)
    pedidos = Pedido.objects.none()
    if cliente is not None:
        pedidos = (
            cliente.pedidos
            .prefetch_related('itens')
            .exclude(status__in=[
                Pedido.Status.ENTREGUE,
                Pedido.Status.CANCELADO,
            ])
        )

    return render(request, 'pedidos/acompanhamento.html', {
        'pedidos': pedidos,
        'etapas_status': [
            Pedido.Status.PENDENTE,
            Pedido.Status.CONFIRMADO,
            Pedido.Status.ENVIADO,
            Pedido.Status.ENTREGUE,
        ],
    })
