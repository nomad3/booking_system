# Generated by Django 4.2 on 2024-09-27 17:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0004_cliente_movimientocliente_alter_venta_cliente'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='preciodinamico',
            options={'ordering': ['-prioridad']},
        ),
        migrations.AlterModelOptions(
            name='reserva',
            options={'ordering': ['-fecha_inicio']},
        ),
        migrations.RenameField(
            model_name='reserva',
            old_name='fecha_reserva',
            new_name='fecha_fin',
        ),
        migrations.RemoveField(
            model_name='preciodinamico',
            name='dia_semana',
        ),
        migrations.RemoveField(
            model_name='preciodinamico',
            name='hora_fin',
        ),
        migrations.RemoveField(
            model_name='preciodinamico',
            name='hora_inicio',
        ),
        migrations.RemoveField(
            model_name='preciodinamico',
            name='mes',
        ),
        migrations.AddField(
            model_name='categoriaproducto',
            name='tipo_duracion',
            field=models.CharField(choices=[('dia', 'Día Completo'), ('hora', 'Hora'), ('minuto', 'Minuto')], default='dia', max_length=10),
        ),
        migrations.AddField(
            model_name='preciodinamico',
            name='tipo_regla',
            field=models.CharField(choices=[('fecha', 'Fecha'), ('hora', 'Hora'), ('dia_semana', 'Día de la Semana'), ('mes', 'Mes')], default='fecha', max_length=20),
        ),
        migrations.AddField(
            model_name='preciodinamico',
            name='valor_regla',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_inicio',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='correo_electronico',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='preciodinamico',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='preciodinamico',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='precios_dinamicos', to='ventas.producto'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='ventas.cliente'),
        ),
        migrations.AddIndex(
            model_name='categoriaproducto',
            index=models.Index(fields=['nombre'], name='ventas_cate_nombre_389748_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['nombre'], name='ventas_clie_nombre_134519_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientocliente',
            index=models.Index(fields=['fecha'], name='ventas_movi_fecha_79f526_idx'),
        ),
        migrations.AddIndex(
            model_name='pago',
            index=models.Index(fields=['venta', 'fecha_pago'], name='ventas_pago_venta_i_281a17_idx'),
        ),
        migrations.AddIndex(
            model_name='preciodinamico',
            index=models.Index(fields=['tipo_regla', 'valor_regla'], name='ventas_prec_tipo_re_c54c42_idx'),
        ),
        migrations.AddIndex(
            model_name='preciodinamico',
            index=models.Index(fields=['fecha_inicio'], name='ventas_prec_fecha_i_10393f_idx'),
        ),
        migrations.AddIndex(
            model_name='preciodinamico',
            index=models.Index(fields=['fecha_fin'], name='ventas_prec_fecha_f_065c70_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['nombre'], name='ventas_prod_nombre_c9f126_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['precio_base'], name='ventas_prod_precio__9c7ebb_idx'),
        ),
        migrations.AddIndex(
            model_name='reserva',
            index=models.Index(fields=['producto', 'fecha_inicio', 'fecha_fin'], name='ventas_rese_product_c040e2_idx'),
        ),
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(fields=['fecha_venta'], name='ventas_vent_fecha_v_357f1c_idx'),
        ),
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(fields=['cliente', 'producto'], name='ventas_vent_cliente_d44864_idx'),
        ),
    ]
