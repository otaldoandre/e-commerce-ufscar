from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Pedido(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        ENVIADO = 'enviado', 'Enviado'
        ENTREGUE = 'entregue', 'Entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    class FormaPagamento(models.TextChoices):
        PIX = 'pix', 'Pix'
        CARTAO_CREDITO = 'cartao_credito', 'Cartão de crédito'
        BOLETO = 'boleto', 'Boleto bancário'

    class StatusPagamento(models.TextChoices):
        NAO_PROCESSADO = 'nao_processado', 'Não processado'
        AUTORIZADO = 'autorizado', 'Autorizado'
        RECUSADO = 'recusado', 'Recusado'

    nome_cliente = models.CharField('nome do cliente', max_length=150)
    email_cliente = models.EmailField('e-mail do cliente')
    endereco_entrega = models.TextField('endereço de entrega')
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    total = models.DecimalField('total', max_digits=12, decimal_places=2)
    forma_pagamento = models.CharField(
        'forma de pagamento',
        max_length=20,
        choices=FormaPagamento.choices,
        blank=True,
    )
    status_pagamento = models.CharField(
        'status do pagamento',
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.NAO_PROCESSADO,
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name='cliente cadastrado',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido #{self.pk}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='pedido',
    )
    produto = models.ForeignKey(
        'catalogo.Produto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_pedido',
        verbose_name='produto',
    )
    nome_produto = models.CharField('nome do produto', max_length=200)
    preco_unitario = models.DecimalField(
        'preço unitário',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantidade = models.PositiveIntegerField(
        'quantidade',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f'{self.quantidade} x {self.nome_produto}'
