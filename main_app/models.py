from django.db import models
from django.templatetags.static import static
from django.contrib.auth.models import User

class Anime(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    studio = models.CharField(max_length=100)
    release_year = models.IntegerField()
    description = models.TextField()
    rating = models.FloatField(default=0.0) 
    image_url = models.ImageField(upload_to='anime_images/', blank=True, null=True)

    def get_static_image(self):
        """Returns a static image based on the anime title."""
        static_image_map = {
            "Bleachanime": "images/Bleachanime.png",
            "Death Note": "images/deathnote.png",
            "Fullmetal Alchemist": "images/Fullmetal Alchemist.png",
            "Hellsing": "images/Hellsing.svg",
            "Samurai Champloo": "images/Samurai Champloo.svg",
            "Vinland Saga": "images/Vinland Saga.svg",
        }
        return static(static_image_map.get(self.title, "images/placeholder.png"))

    def __str__(self):
        return self.title

    def update_rating(self):
        """Recalculate and update the average rating based on reviews."""
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            self.rating = round(avg_rating, 1)
            self.save()

    def get_average_rating(self):
        """Returns the average rating without modifying the model."""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0 


class Watchlist(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='watching')

    class Meta:
        unique_together = ('user', 'anime')

    def __str__(self):
        return f"{self.user.username} - {self.anime.title} ({self.status})"


class Review(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(default=5)  
    likes = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_reviews", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
    
    class Meta:
        unique_together = ('anime', 'user'),
        ordering = ["-created_at"] 

    def __str__(self):
        return f"Review by {self.user.username} on {self.anime.title}"
