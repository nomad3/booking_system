from django import forms
from .models import ReservaProducto


class ReservaProductoForm(forms.ModelForm):
    class Meta:
        model = ReservaProducto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReservaProductoForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.producto and not self.instance.producto.es_reservable:
            self.fields.pop('fecha_agendamiento')