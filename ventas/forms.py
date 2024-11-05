from django import forms
from .models import ReservaProducto, Pago, ReservaServicio, DetalleCompra, Producto  # Asegúrate de importar todos los modelos necesarios
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

class ReservaProductoForm(forms.ModelForm):
    class Meta:
        model = ReservaProducto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReservaProductoForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.producto and not self.instance.producto.es_reservable:
            self.fields.pop('fecha_agendamiento')

        # Definir opciones de horas para cada tipo de servicio
        if 'servicio' in self.initial:
            servicio = self.initial['servicio']
            if servicio.tipo == 'cabañas':
                self.fields['hora'].choices = [
                    ('16:00', '16:00'),
                ]
            elif servicio.tipo == 'tinas':
                self.fields['hora'].choices = [
                    ('14:00', '14:00'),
                    ('14:30', '14:30'),
                    ('17:00', '17:00'),
                    ('19:00', '19:00'),
                    ('19:30', '19:30'),
                    ('21:30', '21:30'),
                    ('22:00', '22:00'),
                ]
            elif servicio.tipo == 'masajes':
                self.fields['hora'].choices = [
                    ('13:00', '13:00'),
                    ('14:15', '14:15'),
                    ('15:30', '15:30'),
                    ('16:45', '16:45'),
                    ('18:00', '18:00'),
                    ('19:15', '19:15'),
                    ('20:30', '20:30'),
                ]

class DetalleCompraForm(forms.ModelForm):
    nuevo_producto = forms.CharField(
        max_length=100, 
        required=False, 
        label='Nuevo Producto',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'nuevo_producto', 'descripcion', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        nuevo_producto = cleaned_data.get('nuevo_producto')

        if not producto and not nuevo_producto:
            raise ValidationError("Debe seleccionar un producto existente o ingresar uno nuevo.")

        if nuevo_producto:
            producto, created = Producto.objects.get_or_create(nombre=nuevo_producto)
            cleaned_data['producto'] = producto

        return cleaned_data

class ReservaServicioInlineForm(forms.ModelForm):
    class Meta:
        model = ReservaServicio
        fields = ['servicio', 'fecha_agendamiento', 'cantidad_personas', 'estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'fecha_agendamiento': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'cantidad_personas': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_fecha_agendamiento(self):
        """
        Convertir el campo `fecha_agendamiento` en un objeto datetime si es necesario.
        """
        fecha_agendamiento = self.cleaned_data.get('fecha_agendamiento')

        # Verificar si fecha_agendamiento es un string y convertirlo a datetime
        if isinstance(fecha_agendamiento, str):
            try:
                fecha_agendamiento = datetime.strptime(fecha_agendamiento, '%Y-%m-%d %H:%M')
                fecha_agendamiento = timezone.make_aware(fecha_agendamiento)  # Asegurarnos de que sea "aware"
            except ValueError:
                raise forms.ValidationError("El formato de la fecha de agendamiento no es válido. Debe ser YYYY-MM-DD HH:MM.")
        
        return fecha_agendamiento

class PagoInlineForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['fecha_pago', 'monto', 'metodo_pago', 'giftcard']  # Eliminado 'usuario'
        widgets = {
            'fecha_pago': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'giftcard': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        giftcard = cleaned_data.get('giftcard')
        monto = cleaned_data.get('monto')

        if metodo_pago == 'giftcard':
            if not giftcard:
                raise ValidationError("Debe seleccionar una gift card para este método de pago.")
            if giftcard.monto_disponible < monto:
                raise ValidationError("El monto excede el saldo disponible en la gift card.")
            if giftcard.fecha_vencimiento < timezone.now().date():
                raise ValidationError("La gift card ha expirado.")
        else:
            if giftcard:
                raise ValidationError("No debe seleccionar una gift card para este método de pago.")

        return cleaned_data