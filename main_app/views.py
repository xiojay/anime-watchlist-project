from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Anime, Review, Watchlist
from .forms import ReviewForm, CustomUserCreationForm, WatchlistForm

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
    reviews = anime.reviews.all() 

    return render(request, "shows/details.html", {"anime": anime, "reviews": reviews})

class AnimeCreate(CreateView):
    model = Anime
    fields = '__all__'  
    template_name = 'shows/anime_form.html'  
    success_url = '/shows/'

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('home')  
    else:
        form = CustomUserCreationForm()
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

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_review(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.anime = anime
            review.user = request.user 
            review.save()
            return redirect('anime-detail', anime_id=anime.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review.html', {'form': form, 'anime': anime})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        return redirect("anime-detail", anime_id=review.anime.id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            review.anime.update_rating()
            return redirect("anime-detail", anime_id=review.anime.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/edit_review.html", {"form": form, "review": review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user == review.user:
        anime_id = review.anime.id
        review.delete()
        review.anime.update_rating() 
        return redirect("anime-detail", anime_id=anime_id)
    else:
        return redirect("anime-detail", anime_id=review.anime.id)

@login_required
def add_to_watchlist(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user, anime=anime)

    if created:
        return redirect('anime-detail', anime_id=anime.id)
    else:
        return redirect('anime-detail', anime_id=anime.id) 

@login_required
def update_watchlist(request, anime_id):
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)

    if request.method == 'POST':
        form = WatchlistForm(request.POST, instance=watchlist_entry)
        if form.is_valid():
            form.save()
            return redirect('anime-detail', anime_id=anime_id)
    else:
        form = WatchlistForm(instance=watchlist_entry)

    return render(request, 'watchlist/update_watchlist.html', {'form': form, 'anime': watchlist_entry.anime})

@login_required
def remove_from_watchlist(request, anime_id):
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)

    if request.method == 'POST':
        watchlist_entry.delete()
        return redirect('anime-detail', anime_id=anime_id)

    return render(request, 'watchlist/remove_confirm.html', {'anime': watchlist_entry.anime})