from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField('nome', max_length=100, unique=True)
    descricao = models.TextField('descrição', blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField('nome', max_length=200)
    descricao = models.TextField('descrição', blank=True)
    preco = models.DecimalField(
        'preço',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estoque = models.PositiveIntegerField('estoque', default=0)
    imagem = models.ImageField('imagem', upload_to='produtos/', blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='produtos',
        verbose_name='categoria',
    )
    ativo = models.BooleanField('ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.nome
