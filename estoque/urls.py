from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('autores/', views.AutorSearchFormListView.as_view(), name = 'autor-list'),
    path('autores/novo/', views.AutorCreateView.as_view(), name = 'autor-create'),
    path('autores/<int:pk>/', views.AutorUpdateView.as_view(), name = 'autor-update'),
    path('autores/remover/<int:pk>/', views.AutorDeleteView.as_view(), name = 'autor-delete'),
    path('livros/', views.LivroSearchFormListView.as_view(), name = 'livro-list'),
    path('livros/novo/', views.LivroCreateView.as_view(), name = 'livro-create'),
    path('livros/<int:pk>/', views.LivroUpdateView.as_view(), name = 'livro-update'),
    path('livros/remover/<int:pk>/', views.LivroDeleteView.as_view(), name = 'livro-delete'),
    path('livros.json', views.LivroJsonListView.as_view(), name = 'livro-json-list'),
    path('autores.json', views.AutorJsonListView.as_view(), name = 'autor-json-list'),
    path('autores/taken/', views.autor_nome_registrado, name = 'autor-taken'),
    url(r'^login/$', auth_views.LoginView.as_view(), name = 'login'),
    url(r'^logout/$', auth_views.LogoutView, name = 'logout'),
    url(r'^admin/', admin.site.urls),
]
