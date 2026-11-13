from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='pontos_fidelidade',
            field=models.PositiveIntegerField(
                default=0,
                verbose_name='pontos de fidelidade',
            ),
        ),
    ]
