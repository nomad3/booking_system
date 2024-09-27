# Generated by Django 4.2 on 2024-09-27 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0008_remove_cliente_direccion_pago_cliente_pago_venta_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VentaReserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_reserva', models.DateTimeField(blank=True, null=True)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('pagado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('saldo_pendiente', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('parcial', 'Parcialmente Pagado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.cliente')),
            ],
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='reserva',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='reserva',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='venta',
        ),
        migrations.RemoveField(
            model_name='reservaproducto',
            name='reserva',
        ),
        migrations.AddField(
            model_name='reservaproducto',
            name='fecha_agendamiento',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Reserva',
        ),
        migrations.DeleteModel(
            name='Venta',
        ),
        migrations.AddField(
            model_name='ventareserva',
            name='productos',
            field=models.ManyToManyField(through='ventas.ReservaProducto', to='ventas.producto'),
        ),
        migrations.AddField(
            model_name='pago',
            name='venta_reserva',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='ventas.ventareserva'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservaproducto',
            name='venta_reserva',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reservaprodutos', to='ventas.ventareserva'),
            preserve_default=False,
        ),
    ]
