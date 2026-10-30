from django.core.management.base import BaseCommand

from catalogo.models import Categoria, Produto


CATALOGO_INICIAL = {
    'Eletrônicos': [
        ('Fone de ouvido Bluetooth', 'Fone sem fio com microfone e bateria de longa duração.', '149.90', 25),
        ('Carregador USB-C', 'Carregador rápido compatível com celulares e tablets.', '79.90', 40),
        ('Teclado sem fio', 'Teclado compacto sem fio para uso doméstico ou profissional.', '119.90', 18),
    ],
    'Casa e decoração': [
        ('Luminária de mesa LED', 'Luminária com três níveis de intensidade para estudo e trabalho.', '89.90', 15),
        ('Garrafa térmica inox', 'Garrafa térmica de aço inoxidável com capacidade de 500 ml.', '59.90', 30),
        ('Organizador multiuso', 'Caixa organizadora dobrável para manter os ambientes em ordem.', '34.90', 22),
    ],
    'Papelaria': [
        ('Caderno universitário', 'Caderno com 200 folhas pautadas e capa dura.', '32.90', 50),
        ('Kit de canetas esferográficas', 'Kit com 10 canetas de escrita suave em cores variadas.', '24.90', 35),
        ('Mochila para notebook', 'Mochila resistente com compartimento acolchoado para notebook.', '129.90', 12),
    ],
}


class Command(BaseCommand):
    help = 'Insere categorias e produtos genéricos para demonstração do catálogo.'

    def handle(self, *args, **options):
        categorias_criadas = 0
        produtos_criados = 0

        for nome_categoria, produtos in CATALOGO_INICIAL.items():
            categoria, categoria_criada = Categoria.objects.get_or_create(
                nome=nome_categoria,
                defaults={'descricao': f'Produtos de {nome_categoria.lower()}.'},
            )
            categorias_criadas += int(categoria_criada)

            for nome, descricao, preco, estoque in produtos:
                _, produto_criado = Produto.objects.get_or_create(
                    nome=nome,
                    defaults={
                        'descricao': descricao,
                        'preco': preco,
                        'estoque': estoque,
                        'categoria': categoria,
                        'ativo': True,
                    },
                )
                produtos_criados += int(produto_criado)

        self.stdout.write(
            self.style.SUCCESS(
                f'Catálogo populado: {categorias_criadas} categorias e '
                f'{produtos_criados} produtos novos.'
            )
        )
