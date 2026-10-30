from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoriaForm, ProdutoForm
from .models import Categoria, Produto


class ProdutoListView(ListView):
    model = Produto
    template_name = 'catalogo/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Produto.objects.select_related('categoria')
        termo = self.request.GET.get('q', '').strip()
        categoria = self.request.GET.get('categoria', '').strip()
        estoque = self.request.GET.get('estoque', '').strip()
        preco_maximo = self.request.GET.get('preco_maximo', '').strip()

        if termo:
            queryset = queryset.filter(
                Q(nome__icontains=termo) | Q(descricao__icontains=termo)
            )
        if categoria.isdigit():
            queryset = queryset.filter(categoria_id=int(categoria))
        if estoque == 'disponivel':
            queryset = queryset.filter(estoque__gt=0)
        elif estoque == 'esgotado':
            queryset = queryset.filter(estoque=0)
        if preco_maximo:
            try:
                queryset = queryset.filter(preco__lte=Decimal(preco_maximo))
            except InvalidOperation:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['filtros'] = self.request.GET
        return context


class ProdutoCreateView(CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'catalogo/produto_form.html'
    success_url = reverse_lazy('catalogo:produto_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso.')
        return super().form_valid(form)


class ProdutoUpdateView(UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'catalogo/produto_form.html'
    success_url = reverse_lazy('catalogo:produto_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso.')
        return super().form_valid(form)


class ProdutoDeleteView(DeleteView):
    model = Produto
    template_name = 'catalogo/produto_confirm_delete.html'
    success_url = reverse_lazy('catalogo:produto_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Produto removido com sucesso.')
        return super().form_valid(form)


class CategoriaListView(ListView):
    model = Categoria
    template_name = 'catalogo/categoria_list.html'
    context_object_name = 'categorias'


class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:categoria_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria cadastrada com sucesso.')
        return super().form_valid(form)


class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:categoria_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso.')
        return super().form_valid(form)
