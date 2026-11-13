from django import forms

from .models import Pedido


class FinalizacaoPedidoForm(forms.Form):
    forma_pagamento = forms.ChoiceField(
        label='Forma de pagamento',
        choices=Pedido.FormaPagamento.choices,
        widget=forms.Select(),
    )


class AcompanhamentoPedidoForm(forms.Form):
    numero_pedido = forms.IntegerField(
        label='Número do pedido',
        min_value=1,
        widget=forms.NumberInput(attrs={'min': 1}),
    )
    email_cliente = forms.EmailField(
        label='E-mail usado na compra',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
