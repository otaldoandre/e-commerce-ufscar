from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('clientes', '0002_cliente_pontos_fidelidade'),
        ('pedidos', '0003_pedido_forma_pagamento_pedido_status_pagamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='cliente',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='pedidos',
                to='clientes.cliente',
                verbose_name='cliente cadastrado',
            ),
        ),
    ]
