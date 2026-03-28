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
    # 'status_estoque' chama a função que criamos abaixo
    list_display = ('nome', 'preco', 'status_estoque') 
    list_editable = ('preco',) # O preço pode editar na lista, o estoque colorido não

    def status_estoque(self, obj):
        if obj.estoque <= 3:
            # Fundo Vermelho para estoque baixo
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{} - REPOR!</span>',
                obj.estoque
            )
        # Fundo Verde para estoque ok
        return format_html(
            '<span style="background-color: #27ae60; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>',
            obj.estoque
        )
    
    # Esta linha deve estar alinhada com o 'def' acima
    status_estoque.short_description = 'Estoque Atual'

# 3. Configuração do Fiado com Trava de Segurança
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
    list_display = ('cliente', 'produto', 'quantidade', 'data', 'pago')
    list_filter = ('pago', 'data')

# 4. Registro do Cliente
admin.site.register(Cliente)