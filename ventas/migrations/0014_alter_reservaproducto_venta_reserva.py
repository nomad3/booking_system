# Generated by Django 4.2 on 2024-10-17 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0013_alter_reservaproducto_venta_reserva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservaproducto',
            name='venta_reserva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservaproductos', to='ventas.ventareserva'),
        ),
    ]
