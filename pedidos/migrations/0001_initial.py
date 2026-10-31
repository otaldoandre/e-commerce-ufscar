import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('catalogo', '0003_produto_imagem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_cliente', models.CharField(max_length=150, verbose_name='nome do cliente')),
                ('email_cliente', models.EmailField(max_length=254, verbose_name='e-mail do cliente')),
                ('endereco_entrega', models.TextField(verbose_name='endereço de entrega')),
                ('status', models.CharField(choices=[('pendente', 'Pendente')], default='pendente', max_length=20, verbose_name='status')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='total')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
            ],
            options={
                'verbose_name': 'pedido',
                'verbose_name_plural': 'pedidos',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_produto', models.CharField(max_length=200, verbose_name='nome do produto')),
                ('preco_unitario', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='preço unitário')),
                ('quantidade', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantidade')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='pedidos.pedido', verbose_name='pedido')),
                ('produto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itens_pedido', to='catalogo.produto', verbose_name='produto')),
            ],
            options={
                'verbose_name': 'item do pedido',
                'verbose_name_plural': 'itens do pedido',
            },
        ),
    ]
