from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, Produto, Fiado

class FiadoForm(forms.ModelForm):
    class Meta:
        model = Fiado
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get('produto')
        quantidade = cleaned_data.get('quantidade')

        # Validação amigável para a interface
        if produto and quantidade and not self.instance.pk:
            if produto.estoque < quantidade:
                raise forms.ValidationError(
                    f"Atenção: Estoque insuficiente! O produto {produto.nome} só tem {produto.estoque} unidades."
                )
        return cleaned_data

@admin.register(Fiado)
class FiadoAdmin(admin.ModelAdmin):
    form = FiadoForm
    list_display = ('cliente', 'produto', 'quantidade', 'data', 'pago')

# Registre os outros se ainda não estiverem lá
admin.site.register(Cliente)
admin.site.register(Produto)