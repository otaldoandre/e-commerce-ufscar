from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalogo.models import Categoria, Produto

from .models import ItemPedido, Pedido


class FinalizacaoPedidoTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nome='Livros')
        self.produto = Produto.objects.create(
            nome='Livro de exemplo',
            preco=Decimal('45.50'),
            estoque=4,
            categoria=categoria,
        )
        self.url = reverse('pedidos:finalizar')
        self.dados_cliente = {
            'nome_cliente': 'Ana Silva',
            'email_cliente': 'ana@example.com',
            'endereco_entrega': 'Rua das Flores, 123',
        }

    def colocar_no_carrinho(self, quantidade=1):
        session = self.client.session
        session['carrinho'] = {str(self.produto.pk): quantidade}
        session.save()

    def test_exibe_formulario_e_resumo_do_carrinho(self):
        self.colocar_no_carrinho()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Finalizar compra')
        self.assertContains(response, self.produto.nome)
        self.assertContains(response, 'name="email_cliente"')

    def test_finaliza_pedido_registra_itens_e_atualiza_estoque(self):
        self.colocar_no_carrinho(2)

        response = self.client.post(self.url, self.dados_cliente)

        pedido = Pedido.objects.get()
        item = ItemPedido.objects.get(pedido=pedido)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pedido recebido')
        self.assertEqual(pedido.nome_cliente, 'Ana Silva')
        self.assertEqual(pedido.total, Decimal('91.00'))
        self.assertEqual(item.nome_produto, self.produto.nome)
        self.assertEqual(item.preco_unitario, Decimal('45.50'))
        self.assertEqual(item.quantidade, 2)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 2)
        self.assertNotIn('carrinho', self.client.session)

    def test_nao_cria_pedido_com_estoque_insuficiente(self):
        self.colocar_no_carrinho(5)

        response = self.client.post(self.url, self.dados_cliente)

        self.assertRedirects(response, reverse('carrinho:detalhe'))
        self.assertFalse(Pedido.objects.exists())
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 4)
        self.assertEqual(self.client.session['carrinho'], {str(self.produto.pk): 5})

    def test_dados_invalidos_nao_criam_pedido(self):
        self.colocar_no_carrinho()

        response = self.client.post(self.url, {
            **self.dados_cliente,
            'email_cliente': 'email-invalido',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Pedido.objects.exists())
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 4)

    def test_carrinho_vazio_nao_pode_ser_finalizado(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('carrinho:detalhe'))
        self.assertFalse(Pedido.objects.exists())
