from django.db import models

# Create your models here.
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=500)
    poster_url = models.URLField(max_length=500, blank=True, default='')
    last_fetched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title