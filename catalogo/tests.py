from decimal import Decimal
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from .models import Categoria, Produto


class CatalogoTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Eletrônicos')
        self.produto = Produto.objects.create(
            nome='Notebook UFSCar',
            descricao='Computador para estudos',
            preco=Decimal('2500.00'),
            estoque=4,
            categoria=self.categoria,
        )

    def test_cadastra_produto(self):
        arquivo = BytesIO()
        Image.new('RGB', (1, 1), color='white').save(arquivo, format='PNG')
        imagem = SimpleUploadedFile(
            'mouse.png',
            arquivo.getvalue(),
            content_type='image/png',
        )
        response = self.client.post(reverse('catalogo:produto_criar'), {
            'nome': 'Mouse',
            'descricao': 'Mouse sem fio',
            'preco': '80.00',
            'estoque': '10',
            'categoria': self.categoria.pk,
            'ativo': 'on',
            'imagem': imagem,
        })
        self.assertRedirects(response, reverse('catalogo:produto_lista'))
        self.assertTrue(Produto.objects.filter(nome='Mouse').exists())

    def test_produto_pode_ser_cadastrado_com_imagem(self):
        arquivo = BytesIO()
        Image.new('RGB', (1, 1), color='white').save(arquivo, format='PNG')
        imagem = SimpleUploadedFile(
            'produto.png',
            arquivo.getvalue(),
            content_type='image/png',
        )
        response = self.client.post(reverse('catalogo:produto_criar'), {
            'nome': 'Produto com imagem',
            'preco': '10.00',
            'estoque': '1',
            'categoria': self.categoria.pk,
            'imagem': imagem,
        })
        self.assertRedirects(response, reverse('catalogo:produto_lista'))
        self.assertTrue(Produto.objects.get(nome='Produto com imagem').imagem.name.startswith('produtos/'))

    def test_edita_produto(self):
        response = self.client.post(
            reverse('catalogo:produto_editar', args=[self.produto.pk]),
            {'nome': 'Notebook atualizado', 'descricao': '', 'preco': '2200.00', 'estoque': '2', 'categoria': self.categoria.pk, 'ativo': 'on'},
        )
        self.assertRedirects(response, reverse('catalogo:produto_lista'))
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.nome, 'Notebook atualizado')

    def test_remove_produto(self):
        response = self.client.post(reverse('catalogo:produto_remover', args=[self.produto.pk]))
        self.assertRedirects(response, reverse('catalogo:produto_lista'))
        self.assertFalse(Produto.objects.filter(pk=self.produto.pk).exists())

    def test_busca_e_filtra_produtos(self):
        Produto.objects.create(nome='Caderno', preco=Decimal('30.00'), estoque=0, categoria=self.categoria)
        response = self.client.get(reverse('catalogo:produto_lista'), {'q': 'notebook'})
        self.assertContains(response, 'Notebook UFSCar')
        self.assertNotContains(response, 'Caderno')
        response = self.client.get(reverse('catalogo:produto_lista'), {'estoque': 'esgotado'})
        self.assertContains(response, 'Caderno')
        self.assertNotContains(response, 'Notebook UFSCar')
