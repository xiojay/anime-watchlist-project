from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    path('shows/', views.shows_index, name='shows-index'),
    path('shows/create/', views.AnimeCreate.as_view(), name='show-create'), 
    path('shows/<int:anime_id>/', views.anime_detail, name='anime-detail'),

    path('signin/', views.signin, name='signin'), 
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('shows/<int:anime_id>/review/', views.add_review, name='add-review'),
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit-review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete-review'),

    path('shows/<int:anime_id>/watchlist/add/', views.add_to_watchlist, name='add-watchlist'),
    path('shows/<int:anime_id>/watchlist/update/', views.update_watchlist, name='update-watchlist'),
    path('shows/<int:anime_id>/watchlist/remove/', views.remove_from_watchlist, name='remove-watchlist'),
    path('watchlist/', views.watchlist, name='watchlist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
