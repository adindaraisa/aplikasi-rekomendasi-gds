from django.urls import path
from app.views.degree_views import rekomendasi_paper_populer
from app.views.views import index

urlpatterns = [
    path('', index, name='index'),
    path('paper-populer', rekomendasi_paper_populer, name='paper-populer'),
]