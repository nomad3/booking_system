# Generated by Django 4.2 on 2024-10-07 21:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ventas', '0009_alter_pago_monto_alter_producto_precio_base_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimientocliente',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
