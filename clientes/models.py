from django.db import models


class Cliente(models.Model):
    usuario = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='cliente',
        null=True,
        blank=True,
        verbose_name='usuário',
    )
    nome = models.CharField('nome completo', max_length=150)
    email = models.EmailField('e-mail', unique=True)
    telefone = models.CharField('telefone', max_length=20)
    endereco = models.TextField('endereço')
    pontos_fidelidade = models.PositiveIntegerField(
        'pontos de fidelidade',
        default=0,
    )
    criado_em = models.DateTimeField('cadastrado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    def __str__(self):
        return f'{self.nome} ({self.email})'
