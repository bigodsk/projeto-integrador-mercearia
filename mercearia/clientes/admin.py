from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Cliente, Produto, Fiado

# 1. Configurações de Título do Painel (O "Logotipo")
admin.site.site_header = "MERCEARIA DA NEUSA"
admin.site.index_title = "Painel de Controle de Vendas e Estoque"
admin.site.site_title = "Gestão Neusa"

# 2. Configuração da lista de Produtos com Alerta Visual
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'status_estoque') 
    list_editable = ('preco',) 

    def status_estoque(self, obj):
        if obj.estoque <= 3:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{} - REPOR!</span>',
                obj.estoque
            )
        return format_html(
            '<span style="background-color: #27ae60; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>',
            obj.estoque
        )
    
    status_estoque.short_description = 'Estoque Atual'

# 3. Configuração do Fiado com Trava de Segurança e Cores
class FiadoForm(forms.ModelForm):
    class Meta:
        model = Fiado
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get('produto')
        quantidade = cleaned_data.get('quantidade')

        if produto and quantidade and not self.instance.pk:
            if produto.estoque < quantidade:
                raise forms.ValidationError(
                    f"Atenção: Estoque insuficiente! O produto {produto.nome} só tem {produto.estoque} unidades."
                )
        return cleaned_data

@admin.register(Fiado)
class FiadoAdmin(admin.ModelAdmin):
    form = FiadoForm
    # Adicionamos 'status_pagamento' e mantivemos o 'pago' para evitar o erro de edição
    list_display = ('cliente', 'produto', 'quantidade', 'data', 'status_pagamento', 'pago')
    list_filter = ('pago', 'data')
    list_editable = ('pago',) # Permite dar baixa no fiado direto na lista

    def status_pagamento(self, obj):
        if obj.pago:
            return format_html(
                '<span style="background-color: #2980b9; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">CONCLUÍDO</span>'
            )
        return format_html(
            '<span style="background-color: #c0392b; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">PENDENTE</span>'
        )
    
    status_pagamento.short_description = 'Situação'

# 4. Registro do Cliente
admin.site.register(Cliente)