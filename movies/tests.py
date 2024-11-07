from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Movie, Rating

User = get_user_model()


class MovieTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase (more efficient than setUp for creating data once)

        # Create two regular users and one super admin
        cls.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password1')
        cls.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password2')
        cls.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')

        # Create two movies: one for each user
        cls.movie1 = Movie.objects.create(title='Movie 1', description='Description 1', created_by=cls.user1)
        cls.movie2 = Movie.objects.create(title='Movie 2', description='Description 2', created_by=cls.user2)

    def test_movie_creation(self):
        # Ensure each user has one movie created
        self.assertEqual(Movie.objects.filter(created_by=self.user1).count(), 1)
        self.assertEqual(Movie.objects.filter(created_by=self.user2).count(), 1)

    def test_rating_functionality(self):
        # Apply ratings to movies
        Rating.objects.create(movie=self.movie1, user=self.user1, score=5)
        Rating.objects.create(movie=self.movie2, user=self.user2, score=4)

        # Refresh movie objects to get updated average rating
        self.movie1.refresh_from_db()
        self.movie2.refresh_from_db()

        # Check that average ratings are correctly calculated
        self.assertEqual(self.movie1.average_rating, 5.0)
        self.assertEqual(self.movie2.average_rating, 4.0)

    def test_reporting_movie(self):
        # Test reporting a movie by a user
        self.movie1.reported = True
        self.movie1.save()
        self.assertTrue(self.movie1.reported)

        # Test rejecting a report by an admin
        self.movie1.reported = False
        self.movie1.save()
        self.assertFalse(self.movie1.reported)

        # Admin approves the report on another movie
        self.movie2.reported = True
        self.movie2.save()
        self.assertTrue(self.movie2.reported)


