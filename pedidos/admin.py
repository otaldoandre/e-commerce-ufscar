from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    can_delete = False
    readonly_fields = [
        'produto',
        'nome_produto',
        'preco_unitario',
        'quantidade',
    ]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_cliente', 'email_cliente', 'status', 'total', 'criado_em']
    list_filter = ['status', 'criado_em']
    list_editable = ['status']
    search_fields = ['nome_cliente', 'email_cliente']
    readonly_fields = [
        'nome_cliente',
        'email_cliente',
        'endereco_entrega',
        'total',
        'criado_em',
    ]
    inlines = [ItemPedidoInline]

    def has_delete_permission(self, request, obj=None):
        return False
