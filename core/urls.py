# Em seu_projeto/urls.py (o arquivo principal)

from django.contrib import admin
from django.urls import path, include
from secretaria import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('secretaria/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('secretaria/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('media/<int:aluno_id>/<str:disciplina>/', views.media_aluno_disciplina, name='media_aluno_disciplina'),
    path('calendario/', views.calendario_academico, name='calendario_academico'),

    path('', include('secretaria.urls')),
]