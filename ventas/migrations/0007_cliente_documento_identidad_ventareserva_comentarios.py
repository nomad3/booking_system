# Generated by Django 4.2 on 2024-10-03 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0006_alter_pago_metodo_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='documento_identidad',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='ID/DNI/Passport/RUT'),
        ),
        migrations.AddField(
            model_name='ventareserva',
            name='comentarios',
            field=models.TextField(blank=True, null=True),
        ),
    ]
