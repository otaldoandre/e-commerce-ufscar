from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalogo.models import Categoria, Produto


class CarrinhoTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nome='Eletrônicos')
        self.produto = Produto.objects.create(
            nome='Mouse',
            preco=Decimal('80.00'),
            estoque=3,
            categoria=categoria,
        )

    def test_adiciona_produto_ao_carrinho(self):
        response = self.client.post(
            reverse('carrinho:adicionar', args=[self.produto.pk]),
            {'next': reverse('catalogo:produto_lista')},
        )

        self.assertRedirects(response, reverse('catalogo:produto_lista'))
        self.assertEqual(self.client.session['carrinho'], {str(self.produto.pk): 1})

    def test_adicionar_novamente_incrementa_quantidade(self):
        url = reverse('carrinho:adicionar', args=[self.produto.pk])
        self.client.post(url)
        self.client.post(url)

        self.assertEqual(self.client.session['carrinho'], {str(self.produto.pk): 2})

    def test_nao_adiciona_produto_esgotado(self):
        self.produto.estoque = 0
        self.produto.save()

        self.client.post(reverse('carrinho:adicionar', args=[self.produto.pk]))

        self.assertNotIn('carrinho', self.client.session)

    def test_exibe_itens_e_total_do_carrinho(self):
        self.client.post(reverse('carrinho:adicionar', args=[self.produto.pk]))

        response = self.client.get(reverse('carrinho:detalhe'))

        self.assertContains(response, self.produto.nome)
        self.assertContains(response, 'R$ 80.00')
        self.assertContains(response, 'Finalizar compra')

    def test_remove_produto_do_carrinho(self):
        self.client.post(reverse('carrinho:adicionar', args=[self.produto.pk]))

        response = self.client.post(
            reverse('carrinho:remover', args=[self.produto.pk]),
        )

        self.assertRedirects(response, reverse('carrinho:detalhe'))
        self.assertEqual(self.client.session.get('carrinho', {}), {})

    def test_remocao_exige_post(self):
        self.client.post(reverse('carrinho:adicionar', args=[self.produto.pk]))

        response = self.client.get(
            reverse('carrinho:remover', args=[self.produto.pk]),
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session['carrinho'], {str(self.produto.pk): 1})
