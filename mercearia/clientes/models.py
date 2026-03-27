from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)
    # Removi o estoque daqui, pois o cliente não tem estoque
    
    def __str__(self):
        return self.nome
    
    def divida_total(self):
        total = 0
        fiados = self.fiado_set.filter(pago=False)
        for f in fiados:
            total += f.quantidade * f.produto.preco
        return total

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    # O estoque deve ficar aqui!
    estoque = models.IntegerField(default=0) 

    def __str__(self):
        return self.nome

from django.core.exceptions import ValidationError # Importante adicionar esse import no topo!

class Fiado(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data = models.DateField(auto_now_add=True)
    pago = models.BooleanField(default=False)

    def total(self):
        return self.quantidade * self.produto.preco

    def save(self, *args, **kwargs):
        # LÓGICA DE TRAVA: Se for uma venda nova
        if not self.pk:
            # 1. Verifica se tem estoque suficiente
            if self.produto.estoque < self.quantidade:
                raise ValidationError(
                    f"Estoque insuficiente! O produto {self.produto.nome} só tem {self.produto.estoque} unidades."
                )
            
            # 2. Se tiver estoque, desconta e salva o produto
            self.produto.estoque -= self.quantidade
            self.produto.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.produto}"