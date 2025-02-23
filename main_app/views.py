from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Anime, Review, Watchlist
from .forms import ReviewForm, CustomUserCreationForm, WatchlistForm

def home(request):
    """Show featured shows for non-logged-in users, and watchlist for logged-in users"""
    featured_shows = Anime.objects.order_by('-rating')[:4]  
    watchlist_items = None

    if request.user.is_authenticated:
        watchlist_items = Watchlist.objects.filter(user=request.user)

    return render(request, 'home.html', {
        'top_anime': featured_shows,
        'watchlist_items': watchlist_items
    })

def about(request):
    return render(request, 'about.html')

def shows_index(request):
    """Show all anime, filterable via search query"""
    query = request.GET.get('q', '') 
    shows = Anime.objects.filter(title__icontains=query).order_by('-rating') if query else Anime.objects.all().order_by('-rating')
    
    return render(request, 'shows/index.html', {'shows': shows, 'query': query})

def anime_detail(request, anime_id):
    """Display anime details, reviews, and watchlist status"""
    anime = get_object_or_404(Anime, id=anime_id)
    reviews = anime.reviews.all()
    watchlist_entry = Watchlist.objects.filter(user=request.user, anime=anime).first() if request.user.is_authenticated else None

    return render(request, "shows/details.html", {
        "anime": anime, 
        "reviews": reviews, 
        "watchlist_entry": watchlist_entry
    })

class AnimeCreate(CreateView):
    model = Anime
    fields = '__all__'  
    template_name = 'shows/anime_form.html'  
    success_url = '/shows/'

def signup(request):
    """User signup"""
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
    """User login"""
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
    """User logout"""
    logout(request)
    return redirect('home')

@login_required
def add_review(request, anime_id):
    """Add a review to an anime"""
    anime = get_object_or_404(Anime, id=anime_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.anime = anime
            review.user = request.user 
            review.save()
            messages.success(request, "Your review has been added!")  
            return redirect('anime-detail', anime_id=anime.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review.html', {'form': form, 'anime': anime})

@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        return redirect("anime-detail", anime_id=review.anime.id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            review.anime.update_rating()
            messages.success(request, "Your review has been updated!")  
            return redirect("anime-detail", anime_id=review.anime.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/edit_review.html", {"form": form, "review": review})

@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id)

    if request.user == review.user:
        anime_id = review.anime.id
        review.delete()
        review.anime.update_rating() 
        messages.success(request, "Your review has been deleted.") 
        return redirect("anime-detail", anime_id=anime_id)

    return redirect("anime-detail", anime_id=review.anime.id)

@login_required
def add_to_watchlist(request, anime_id):
    """Add anime to watchlist and reload the same page"""
    anime = get_object_or_404(Anime, id=anime_id)
    Watchlist.objects.get_or_create(user=request.user, anime=anime)
    messages.success(request, f"{anime.title} added to your watchlist!") 
    return redirect('anime-detail', anime_id=anime.id) 

@login_required
def remove_from_watchlist(request, anime_id):
    """Remove anime from watchlist and reload the same page"""
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)
    anime = watchlist_entry.anime  # ✅ Define anime before redirect
    watchlist_entry.delete()
    messages.success(request, f"{anime.title} removed from your watchlist.")  
    return redirect('anime-detail', anime_id=anime.id) 

@login_required
def update_watchlist(request, anime_id):
    """Update anime watchlist status"""
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)

    if request.method == 'POST':
        form = WatchlistForm(request.POST, instance=watchlist_entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Watchlist status updated!")  
            return redirect('anime-detail', anime_id=anime_id)
    else:
        form = WatchlistForm(instance=watchlist_entry)

    return render(request, 'watchlist/update_watchlist.html', {'form': form, 'anime': watchlist_entry.anime})

@login_required
def watchlist(request):
    """View all anime in the user's watchlist"""
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, 'watchlist/watchlist.html', {'watchlist_items': watchlist_items})
