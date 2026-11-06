from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='status',
            field=models.CharField(
                choices=[
                    ('pendente', 'Pendente'),
                    ('confirmado', 'Confirmado'),
                    ('enviado', 'Enviado'),
                    ('entregue', 'Entregue'),
                    ('cancelado', 'Cancelado'),
                ],
                default='pendente',
                max_length=20,
                verbose_name='status',
            ),
        ),
    ]
