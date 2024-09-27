# ventas/forms.py

from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        es_reservable = cleaned_data.get('es_reservable')
        valor = cleaned_data.get('duracion_reserva_valor')
        unidad = cleaned_data.get('duracion_reserva_unidad')

        if es_reservable:
            if not valor or not unidad:
                raise forms.ValidationError('Debe especificar tanto el valor como la unidad de duración de la reserva si el producto es reservable.')
        return cleaned_data
