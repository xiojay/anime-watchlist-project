from django.shortcuts import get_object_or_404, render
from .models import Anime  # Import the Anime model

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def shows_index(request):
    query = request.GET.get('q', '')
    if query:
        shows = Anime.objects.filter(title__icontains=query)
    else:
        shows = Anime.objects.all()

    return render(request, 'shows/index.html', {'shows': shows, 'query': query})

def anime_detail(request, anime_id):
    anime = Anime.objects.get( id=anime_id)
    return render(request, 'shows/details.html', {'anime': anime})