from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.urls import reverse

from .models import Cliente, Produto, Fiado
from .forms import ClienteForm, ProdutoForm, FiadoForm


def dashboard(request):
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_produtos': Produto.objects.count(),
        'fiados_pendentes': Fiado.objects.filter(pago=False).count(),
        'produtos_criticos': Produto.objects.filter(estoque__lte=3).count(),
    }
    return render(request, 'clientes/dashboard.html', context)


def lista_clientes(request):
    clientes = Cliente.objects.prefetch_related(
        Prefetch('fiado_set', queryset=Fiado.objects.select_related('produto'))
    )
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})


def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    fiados = cliente.fiado_set.select_related('produto').order_by('-data')
    return render(request, 'clientes/cliente_detalhe.html', {'cliente': cliente, 'fiados': fiados})


def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado!')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form, 'titulo': 'Novo Cliente'})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente atualizado!')
        return redirect('lista_clientes')
    return render(request, 'clientes/cliente_form.html', {
        'form': form,
        'titulo': f'Editar: {cliente.nome}',
        'cliente': cliente,
    })


def deletar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente removido.')
        return redirect('lista_clientes')
    return render(request, 'clientes/confirmar_deletar.html', {
        'objeto': cliente,
        'voltar_url': reverse('lista_clientes'),
    })


def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'clientes/produtos_list.html', {'produtos': produtos})


def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado!')
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'clientes/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})


def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, instance=produto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Produto atualizado!')
        return redirect('lista_produtos')
    return render(request, 'clientes/produto_form.html', {
        'form': form,
        'titulo': f'Editar: {produto.nome}',
        'produto': produto,
    })


def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto removido.')
        return redirect('lista_produtos')
    return render(request, 'clientes/confirmar_deletar.html', {
        'objeto': produto,
        'voltar_url': reverse('lista_produtos'),
    })


def lista_fiados(request):
    status = request.GET.get('status', '')
    qs = Fiado.objects.select_related('cliente', 'produto').order_by('-data')
    if status == 'pendente':
        qs = qs.filter(pago=False)
    elif status == 'pago':
        qs = qs.filter(pago=True)
    return render(request, 'clientes/fiados_list.html', {'fiados': qs, 'status_filtro': status})


def criar_fiado(request):
    if request.method == 'POST':
        form = FiadoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Fiado registrado!')
                return redirect('lista_fiados')
            except ValidationError as e:
                messages.error(request, e.message)
    else:
        form = FiadoForm()
    return render(request, 'clientes/fiado_form.html', {'form': form, 'titulo': 'Registrar Fiado'})


def editar_fiado(request, pk):
    fiado = get_object_or_404(Fiado, pk=pk)
    form = FiadoForm(request.POST or None, instance=fiado)
    if form.is_valid():
        form.save()
        messages.success(request, 'Fiado atualizado!')
        return redirect('lista_fiados')
    return render(request, 'clientes/fiado_form.html', {'form': form, 'titulo': 'Editar Fiado', 'fiado': fiado})


def deletar_fiado(request, pk):
    fiado = get_object_or_404(Fiado, pk=pk)
    if request.method == 'POST':
        fiado.delete()
        messages.success(request, 'Fiado removido.')
        return redirect('lista_fiados')
    return render(request, 'clientes/confirmar_deletar.html', {
        'objeto': fiado,
        'voltar_url': reverse('lista_fiados'),
    })


def pagar_fiado(request, pk):
    fiado = get_object_or_404(Fiado, pk=pk)
    if request.method == 'POST':
        fiado.pago = True
        fiado.save()
        messages.success(request, f'Fiado de {fiado.cliente} marcado como pago!')
    return redirect(request.POST.get('next', reverse('lista_fiados')))
