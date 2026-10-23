from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.ProdutoListView.as_view(), name='produto_lista'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_criar'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_editar'),
    path('produtos/<int:pk>/remover/', views.ProdutoDeleteView.as_view(), name='produto_remover'),
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_criar'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
]
