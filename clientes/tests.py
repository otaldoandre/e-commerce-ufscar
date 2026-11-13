from django.test import TestCase
from django.urls import reverse

from .models import Cliente


class CadastroClienteTests(TestCase):
    def setUp(self):
        self.url = reverse('clientes:cadastro')
        self.dados_cliente = {
            'nome': 'Ana Silva',
            'email': 'ana@example.com',
            'senha': 'senha-segura-123',
            'confirmacao_senha': 'senha-segura-123',
            'telefone': '(16) 99999-9999',
            'endereco': 'Rua das Flores, 123',
        }
        self.dados_cadastro = {
            **self.dados_cliente,
            'senha': 'senha-segura-123',
            'confirmacao_senha': 'senha-segura-123',
        }

    def test_exibe_formulario_de_cadastro(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro de cliente')
        self.assertContains(response, 'name="email"')

    def test_cadastra_cliente(self):
        response = self.client.post(self.url, self.dados_cadastro)

        self.assertRedirects(response, self.url)
        cliente = Cliente.objects.get()
        self.assertEqual(cliente.nome, 'Ana Silva')
        self.assertEqual(cliente.email, 'ana@example.com')
        self.assertTrue(cliente.usuario.check_password('senha-segura-123'))

    def test_cliente_pode_entrar_com_email_e_senha(self):
        self.client.post(self.url, self.dados_cliente)

        response = self.client.post(reverse('clientes:login'), {
            'email': 'ana@example.com',
            'senha': 'senha-segura-123',
        })

        self.assertRedirects(response, reverse('catalogo:produto_lista'))

    def test_historico_exige_login(self):
        response = self.client.get(reverse('clientes:historico'))

        self.assertRedirects(
            response,
            f'{reverse("clientes:login")}?next={reverse("clientes:historico")}',
        )

    def test_nao_cadastra_email_duplicado(self):
        self.client.post(self.url, self.dados_cadastro)

        response = self.client.post(self.url, {
            **self.dados_cadastro,
            'nome': 'Outro cliente',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Já existe um cliente')
        self.assertEqual(Cliente.objects.count(), 1)

    def test_nao_cadastra_email_invalido(self):
        response = self.client.post(self.url, {
            **self.dados_cadastro,
            'email': 'email-invalido',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cliente.objects.exists())
