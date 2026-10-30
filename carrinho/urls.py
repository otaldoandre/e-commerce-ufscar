from django.urls import path

from . import views

app_name = 'carrinho'

urlpatterns = [
    path('', views.detalhe_carrinho, name='detalhe'),
    path('adicionar/<int:pk>/', views.adicionar_ao_carrinho, name='adicionar'),
]
