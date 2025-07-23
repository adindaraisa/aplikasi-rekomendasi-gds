from django.urls import path
from app.views.degree_views import rekomendasi_paper_populer
from app.views.views import index
from app.views.pagerank_views import rekomendasi_paper_berpengaruh
from app.views.knn_views import rekomendasi_paper_detail

urlpatterns = [
    path('', index, name='index'),
    path('paper-populer', rekomendasi_paper_populer, name='paper-populer'),
    path('paper-berpengaruh', rekomendasi_paper_berpengaruh, name='paper-berpengaruh'),
    path('paper/<str:paper_id>/', rekomendasi_paper_detail, name='paper-detail'),
]