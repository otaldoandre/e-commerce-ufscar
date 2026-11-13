from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('nome', models.CharField(max_length=150, verbose_name='nome completo')),
                (
                    'email',
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        verbose_name='e-mail',
                    ),
                ),
                ('telefone', models.CharField(max_length=20, verbose_name='telefone')),
                ('endereco', models.TextField(verbose_name='endereço')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='cadastrado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'cliente',
                'verbose_name_plural': 'clientes',
                'ordering': ['nome'],
            },
        ),
    ]
