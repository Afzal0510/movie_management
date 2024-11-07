
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings

# Example models for User, Movie, and Rating
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    released_at = models.DateTimeField()  # This is the release date of the movie
    duration = models.IntegerField()  # Duration in minutes (or seconds, based on your preference)
    genre = models.CharField(max_length=100)  # Genre, could be a CharField or ForeignKey to another model
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    average_rating = models.FloatField(default=0.0)
    total_rating = models.IntegerField(default=0)
    language = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update average rating after each save
        movie = self.movie
        ratings = movie.rating_set.all()
        movie.average_rating = sum(r.score for r in ratings) / len(ratings)
        movie.save()


class MovieReport(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report by {self.user} on {self.movie}'
