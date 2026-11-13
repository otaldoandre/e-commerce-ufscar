from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Categoria, Produto
from clientes.models import Cliente

from .models import ItemPedido, Pedido


class FinalizacaoPedidoTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='ana@example.com',
            email='ana@example.com',
            password='senha-segura-123',
        )
        Cliente.objects.create(
            usuario=usuario,
            nome='Ana Silva',
            email='ana@example.com',
            telefone='(16) 99999-9999',
            endereco='Rua das Flores, 123',
        )
        self.client.force_login(usuario)
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
        self.assertContains(response, 'name="forma_pagamento"')
        self.assertNotContains(response, 'name="nome_cliente"')
        self.assertNotContains(response, 'name="email_cliente"')
        self.assertNotContains(response, 'name="endereco_entrega"')

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
            'forma_pagamento': Pedido.FormaPagamento.PIX,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Pedido.objects.exists())

    def test_dados_do_pedido_usam_o_cadastro_autenticado(self):
        self.colocar_no_carrinho()

        response = self.client.post(self.url, {
            'forma_pagamento': Pedido.FormaPagamento.PIX,
            'nome_cliente': 'Cliente adulterado',
            'email_cliente': 'outro@example.com',
            'endereco_entrega': 'Endereço adulterado',
        })

        pedido = Pedido.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pedido.nome_cliente, 'Ana Silva')
        self.assertEqual(pedido.email_cliente, 'ana@example.com')
        self.assertEqual(pedido.endereco_entrega, 'Rua das Flores, 123')

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
        usuario = get_user_model().objects.create_user(
            username='ana@example.com',
            email='ana@example.com',
            password='senha-segura-123',
        )
        cliente = Cliente.objects.create(
            usuario=usuario,
            nome='Ana Silva',
            email='ana@example.com',
            telefone='(16) 99999-9999',
            endereco='Rua das Flores, 123',
        )
        self.pedido = Pedido.objects.create(
            cliente=cliente,
            nome_cliente='Ana Silva',
            email_cliente='ana@example.com',
            endereco_entrega='Rua das Flores, 123',
            total=Decimal('45.50'),
            status=Pedido.Status.ENVIADO,
        )
        self.client.force_login(usuario)
        ItemPedido.objects.create(
            pedido=self.pedido,
            nome_produto='Livro de exemplo',
            preco_unitario=Decimal('45.50'),
            quantidade=1,
        )
        self.url = reverse('pedidos:acompanhar')

    def test_exibe_pedidos_em_andamento_do_cliente_logado(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acompanhar pedido')
        self.assertContains(response, 'Enviado')
        self.assertContains(response, 'Livro de exemplo')
        self.assertContains(response, 'status atual')

    def test_nao_exibe_pedidos_entregues_ou_cancelados(self):
        Pedido.objects.create(
            cliente=self.pedido.cliente,
            nome_cliente='Ana Silva',
            email_cliente='ana@example.com',
            endereco_entrega='Rua das Flores, 123',
            total=Decimal('20.00'),
            status=Pedido.Status.ENTREGUE,
        )
        Pedido.objects.create(
            cliente=self.pedido.cliente,
            nome_cliente='Ana Silva',
            email_cliente='ana@example.com',
            endereco_entrega='Rua das Flores, 123',
            total=Decimal('20.00'),
            status=Pedido.Status.CANCELADO,
        )

        response = self.client.get(self.url)

        self.assertContains(response, f'Pedido #{self.pedido.pk}')
        self.assertEqual(response.content.decode().count('Pedido #'), 1)

    def test_acompanhamento_exige_login(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f'{reverse("clientes:login")}?next={self.url}',
        )

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
