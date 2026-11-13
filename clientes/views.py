from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from pedidos.models import Pedido

from .forms import ClienteForm, LoginClienteForm
from .models import Cliente


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cadastro')

    def form_valid(self, form):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        with transaction.atomic():
            usuario = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['senha'],
            )
            form.instance.usuario = usuario
            response = super().form_valid(form)
        messages.success(self.request, 'Cadastro realizado com sucesso.')
        return response


def login_cliente(request):
    form = LoginClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        from django.contrib.auth import get_user_model
        usuario = get_user_model().objects.filter(
            email__iexact=form.cleaned_data['email'],
            is_active=True,
        ).first()
        if usuario is None or not usuario.check_password(form.cleaned_data['senha']):
            form.add_error(None, 'E-mail ou senha inválidos.')
        else:
            login(request, usuario)
            return redirect('catalogo:produto_lista')
    return render(request, 'clientes/login.html', {'form': form})


@login_required
def logout_cliente(request):
    logout(request)
    return redirect('catalogo:produto_lista')


@login_required
def historico_cliente(request):
    cliente = getattr(request.user, 'cliente', None)
    pedidos = Pedido.objects.none() if cliente is None else cliente.pedidos.prefetch_related('itens')
    return render(request, 'clientes/historico.html', {
        'form': None,
        'cliente': cliente,
        'pedidos': pedidos,
    })
