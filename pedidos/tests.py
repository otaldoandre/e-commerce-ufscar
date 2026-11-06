from decimal import Decimal

from django.contrib.auth import get_user_model
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
            'forma_pagamento': Pedido.FormaPagamento.PIX,
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
        self.assertEqual(pedido.status, Pedido.Status.CONFIRMADO)
        self.assertEqual(pedido.forma_pagamento, Pedido.FormaPagamento.PIX)
        self.assertEqual(
            pedido.status_pagamento,
            Pedido.StatusPagamento.AUTORIZADO,
        )
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

    def test_pagamento_com_valor_zero_nao_e_autorizado(self):
        self.colocar_no_carrinho()
        self.produto.preco = Decimal('0.00')
        self.produto.save(update_fields=['preco'])

        response = self.client.post(self.url, self.dados_cliente)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'O valor do pagamento deve ser maior que zero.')
        self.assertFalse(Pedido.objects.exists())
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, 4)
        self.assertIn('carrinho', self.client.session)

    def test_carrinho_vazio_nao_pode_ser_finalizado(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('carrinho:detalhe'))
        self.assertFalse(Pedido.objects.exists())


class AcompanhamentoPedidoTests(TestCase):
    def setUp(self):
        self.pedido = Pedido.objects.create(
            nome_cliente='Ana Silva',
            email_cliente='ana@example.com',
            endereco_entrega='Rua das Flores, 123',
            total=Decimal('45.50'),
            status=Pedido.Status.ENVIADO,
        )
        ItemPedido.objects.create(
            pedido=self.pedido,
            nome_produto='Livro de exemplo',
            preco_unitario=Decimal('45.50'),
            quantidade=1,
        )
        self.url = reverse('pedidos:acompanhar')

    def test_exibe_formulario_de_acompanhamento(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acompanhar pedido')
        self.assertContains(response, 'numero_pedido')

    def test_consulta_pedido_com_numero_e_email_corretos(self):
        response = self.client.post(self.url, {
            'numero_pedido': self.pedido.pk,
            'email_cliente': 'ANA@example.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enviado')
        self.assertContains(response, 'Livro de exemplo')
        self.assertContains(response, 'status atual')

    def test_nao_exibe_pedido_quando_email_nao_corresponde(self):
        response = self.client.post(self.url, {
            'numero_pedido': self.pedido.pk,
            'email_cliente': 'outra@example.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Não foi possível localizar um pedido')
        self.assertNotContains(response, 'Livro de exemplo')

    def test_nao_aceita_numero_de_pedido_invalido(self):
        response = self.client.post(self.url, {
            'numero_pedido': 0,
            'email_cliente': 'ana@example.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Livro de exemplo')

    def test_administrador_pode_atualizar_status_do_pedido(self):
        usuario = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='senha-de-teste',
        )
        self.client.force_login(usuario)

        self.client.post(reverse('admin:pedidos_pedido_changelist'), {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': self.pedido.pk,
            'form-0-status': Pedido.Status.ENTREGUE,
            '_save': 'Salvar',
        })

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.ENTREGUE)
