from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
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

@login_required
def user_profile(request, user_id):
    """Render user profile page"""
    if request.user.id != user_id:
        return redirect('home') 
    return render(request, "profile/user-profile.html")

@login_required
def update_profile(request):
    """Update user profile (username & email)"""
    if request.method == "POST":
        new_username = request.POST.get("username").strip()
        new_email = request.POST.get("email").strip()

        if User.objects.exclude(id=request.user.id).filter(username=new_username).exists():
            messages.error(request, "This username is already taken. Please choose another.")
            return redirect("update-profile")

        request.user.username = new_username
        request.user.email = new_email
        request.user.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect("update-profile")

    return render(request, "profile/user-profile.html")

@login_required
def change_password(request):
    """Allow user to change their password"""
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(old_password):
            messages.error(request, "Incorrect current password.")
            return redirect("change-password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change-password")

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user) 

        messages.success(request, "Your password has been updated successfully!")
        return redirect("update-profile")

    return render(request, "profile/user-profile.html")

def about(request):
    return render(request, 'about.html')

def shows_index(request):
    """Show all anime, filterable via search query"""
    query = request.GET.get('q', '') 
    shows = Anime.objects.filter(title__icontains=query).order_by('-rating') if query else Anime.objects.all().order_by('-rating')
    
    return render(request, 'shows/index.html', {'shows': shows, 'query': query})

def anime_detail(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)
    reviews = anime.reviews.all()
    watchlist_entry = None
    watchlist_form = None
    user_review = None

    if request.user.is_authenticated:
        watchlist_entry = Watchlist.objects.filter(user=request.user, anime=anime).first()
        watchlist_form = WatchlistForm(instance=watchlist_entry)
        user_review = Review.objects.filter(anime=anime, user=request.user).first()

    return render(request, "shows/details.html", {
        "anime": anime, 
        "reviews": reviews, 
        "watchlist_entry": watchlist_entry,
        "watchlist_form": watchlist_form,
        "user_review": user_review,
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
    """Add a review to an anime, preventing duplicate reviews"""
    anime = get_object_or_404(Anime, id=anime_id)
    existing_review = Review.objects.filter(anime=anime, user=request.user).exists()
    if existing_review:
        messages.error(request, "You have already reviewed this anime.")
        return redirect("anime-detail", anime_id=anime.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.anime = anime
            review.user = request.user
            review.save()
            anime.update_rating()
            messages.success(request, "Your review has been successfully added!")
            return redirect("anime-detail", anime_id=anime.id)
        else:
            messages.error(request, "There was an issue adding your review. Please try again.")
    else:
        form = ReviewForm()

    return render(request, "reviews/review.html", {"form": form, "anime": anime})

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

    return render(request, "reviews/edit-review.html", {"form": form, "review": review})

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
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)
        review.dislikes.remove(request.user) 

    return redirect('anime-detail', review.anime.id)

@login_required
def dislike_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user in review.dislikes.all():
        review.dislikes.remove(request.user)
    else:
        review.dislikes.add(request.user)
        review.likes.remove(request.user)
        
    return redirect('anime-detail', review.anime.id)


@login_required
def add_to_watchlist(request, anime_id):
    """Add anime to watchlist and reload the same page"""
    anime = get_object_or_404(Anime, id=anime_id)
    Watchlist.objects.get_or_create(user=request.user, anime=anime)
    messages.success(request, f"{anime.title} added to your watchlist!") 
    return redirect('anime-detail', anime_id=anime.id) 

@login_required
def remove_from_watchlist(request, anime_id):
    """Remove anime from watchlist and reload the watchlist page"""
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)
    anime = watchlist_entry.anime  
    watchlist_entry.delete()
    messages.success(request, f"{anime.title} removed from your watchlist.")  
    return redirect('watchlist') 


@login_required
def update_watchlist(request, anime_id):
    """Update watchlist status without dropdown"""
    watchlist_entry = get_object_or_404(Watchlist, user=request.user, anime_id=anime_id)

    if request.method == "POST":
        new_status = request.POST.get("status", watchlist_entry.status)  
        watchlist_entry.status = new_status
        watchlist_entry.save()
        messages.success(request, "Watchlist status updated!")  
        return redirect("watchlist")  

    return render(request, "watchlist/update_watchlist.html", {"anime": watchlist_entry.anime})


@login_required
def watchlist(request):
    """View all anime in the user's watchlist"""
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, 'watchlist/watchlist.html', {'watchlist_items': watchlist_items})
