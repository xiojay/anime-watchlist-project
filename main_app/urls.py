from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  
urlpatterns = [
    # home & about
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # shows
    path('shows/', views.shows_index, name='shows-index'),
    path('shows/<int:anime_id>/', views.anime_detail, name='anime-detail'),
    path('shows/create/', views.AnimeCreate.as_view(), name='show-create'), 

    # authentication
    path('signin/', views.signin, name='signin'), 
    path('signup/', views.signup, name='signup'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
