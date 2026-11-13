from django.urls import path

from . import views

app_name = 'clientes'

urlpatterns = [
    path('cadastro/', views.ClienteCreateView.as_view(), name='cadastro'),
    path('login/', views.login_cliente, name='login'),
    path('logout/', views.logout_cliente, name='logout'),
    path('historico/', views.historico_cliente, name='historico'),
]
