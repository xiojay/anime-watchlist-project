from django.db import models

from django.db import models

class Anime(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    studio = models.CharField(max_length=100)
    release_year = models.IntegerField()
    description = models.TextField()
    rating = models.FloatField(default=0.0)
    image_url = models.ImageField(upload_to='anime_images/', blank=True, null=True)

    def __str__(self):
        return self.title
