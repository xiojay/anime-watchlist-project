from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Anime 

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def shows_index(request):
    query = request.GET.get('q', '') 
    if query:
        shows = Anime.objects.filter(title__icontains=query).order_by('-rating') 
    else:
        shows = Anime.objects.all().order_by('-rating')  

    return render(request, 'shows/index.html', {'shows': shows, 'query': query})

def anime_detail(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id) 
    return render(request, 'shows/details.html', {'anime': anime})

class AnimeCreate(CreateView):
    model = Anime
    fields = '__all__'  
    template_name = 'shows/anime_form.html'  
    success_url = '/shows/' 
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('home')  
    else:
        form = UserCreationForm()
    return render(request, 'signup/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) 
            return redirect('home') 
    else:
        form = AuthenticationForm()
    return render(request, 'signin/signin.html', {'form': form})
