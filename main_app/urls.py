from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Import views to connect routes to view functions

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shows/', views.shows_index, name='shows-index'),
    path('shows/<int:anime_id>/', views.anime_detail, name='anime-detail'),
]

# ✅ Add this line correctly outside the urlpatterns list
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
