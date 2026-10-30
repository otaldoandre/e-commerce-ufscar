from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='nome')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('criada_em', models.DateTimeField(auto_now_add=True, verbose_name='criada em')),
            ],
            options={
                'verbose_name': 'categoria',
                'verbose_name_plural': 'categorias',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='nome')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='preço')),
                ('estoque', models.PositiveIntegerField(default=0, verbose_name='estoque')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='produtos', to='catalogo.categoria', verbose_name='categoria')),
            ],
            options={
                'verbose_name': 'produto',
                'verbose_name_plural': 'produtos',
                'ordering': ['nome'],
            },
        ),
    ]
