# movies/urls.py
from django.urls import path
from .views import list_all_movies, list_user_movies, view_movie_detail, update_movie, create_movie, rate_movie, \
    report_movie, manage_reported_movies, login_view, register_user, manage_movie_report

urlpatterns = [
    path('signup/',register_user,name='register_user'),
    path('login/',login_view,name='login_view'),
    path('list/', list_all_movies, name='list_all_movies'),
    path('movies/user/', list_user_movies, name='list_user_movies'),
    path('movies/<int:movie_id>/', view_movie_detail, name='view_movie_detail'),
    path('movies/create/', create_movie, name='create_movie'),
    path('movies/<int:movie_id>/update/', update_movie, name='update_movie'),
    path('movies/<int:movie_id>/rate/', rate_movie, name='rate_movie'),
    path('movies/<int:movie_id>/report/', report_movie, name='report_movie'),
    path('movies/reports/manage/', manage_reported_movies, name='manage_reported_movies'),
    path('movie_reports/<int:report_id>/manage/', manage_movie_report, name='manage_movie_report'),
]
