from django.http import JsonResponse
from knox.serializers import UserSerializer, User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utility import generate_access_token, generate_refresh_token, is_admin
from .models import Movie, Rating, MovieReport
from .serializers import MovieSerializer, RatingSerializer, LoginSerializer, MovieReportSerializer
from .utility import is_auth

from django.db.models import Avg

@api_view(['POST'])
def register_user(request):

    """
      Registers a new user. Expects username, email, and password in the request data.
      If valid, creates and returns the user data.
      """
    # Initialize serializer with request data
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    """
    Logs in the user without authenticating.
    """
    # Just retrieve user based on username without password validation (NOT recommended)
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)  # Get the user by username directly
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Generate tokens for the user
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    return Response({
        "access_token": access_token,
        "refresh_token": refresh_token
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@is_auth
def list_all_movies(request):
    """
        Retrieves a list of all movies in the system.

        Requires:
            - Authentication token in headers.

        Returns:
            - List of all movies (200).
        """

    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@is_auth
def list_user_movies(request):
    """
       Retrieves movies created by the authenticated user.

       Requires:
           - Authentication token in headers.

       Returns:
           - List of movies created by the user (200).
       """

    user = request.user
    movies = Movie.objects.filter(created_by=user)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@is_auth
def view_movie_detail(request, movie_id):
    """
       Retrieves detailed information about a specific movie.

       Expects:
           - `movie_id`: ID of the movie to retrieve.


      """

    try:
        movie = Movie.objects.get(id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Movie.DoesNotExist:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@is_auth
def create_movie(request):
    # Extract data from request
    title = request.data.get("title")
    description = request.data.get("description")
    released_at = request.data.get("released_at")
    duration = request.data.get("duration")
    genre = request.data.get("genre")
    language = request.data.get("language")

    # Create the movie with authenticated user as created_by
    movie = Movie(
        title=title,
        description=description,
        released_at=released_at,
        duration=duration,
        genre=genre,
        language=language,
        created_by=request.user  # `request.user` is the full User object here
    )
    movie.save()

    return Response({"message": "Movie created successfully!"}, status=201)


@api_view(['PUT'])
@is_auth
def update_movie(request, movie_id):
    """
        Updates an existing movie.

        Expects:
            - `movie_id`: ID of the movie to update.
    """

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is the creator of the movie
    if movie.created_by != request.user:
        return Response({"message": "Only the creator or an admin can update this movie."},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = MovieSerializer(movie, data=request.data, partial=True, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        # Print serializer errors to debug
        print(serializer.errors)  # This will print to the console or logs
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@is_auth
def rate_movie(request, movie_id):
    """
    Allow an authenticated user to add or update their rating for a movie.
    """
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure 'score' is part of the request data
    data = request.data.copy()
    data['user_id'] = request.user.id  # Add user_id to the data

    # Now, pass the data to the serializer
    serializer = RatingSerializer(data=data, context={'request': request})

    if serializer.is_valid():
        # Save the rating with movie and user details
        serializer.save(movie=movie, user_id=request.user.id)  # Ensure the correct field is passed
        return Response({"message": "Rating submitted successfully", "data": serializer.data},
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@is_auth
def report_movie(request, movie_id):
    """
    Allows an authenticated user to report a movie.
    """
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MovieReportSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(movie=movie)
        return Response({"message": "Movie reported successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@is_auth
def manage_reported_movies(request):
    """
    Allows an admin to view and update the status of reported movies.
    """
    if not request.user.is_staff:
        return Response({"message": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # Get all reported movies with status 'PENDING'
        reports = MovieReport.objects.filter(status='PENDING')
        serializer = MovieReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        # Update a specific report's status
        report_id = request.data.get('report_id')
        new_status = request.data.get('status')

        if new_status not in dict(MovieReport.STATUS_CHOICES):
            return Response({"message": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = MovieReport.objects.get(id=report_id)
            report.status = new_status
            report.save()
            return Response({"message": "Report status updated successfully"}, status=status.HTTP_200_OK)
        except MovieReport.DoesNotExist:
            return Response({"message": "Report not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@is_admin  # A decorator to ensure the user is an admin
def manage_movie_report(request, report_id, status=None):
    try:
        report = MovieReport.objects.get(id=report_id)
    except MovieReport.DoesNotExist:
        return Response({"message": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

    status = request.data.get('status')
    if status not in ['APPROVED', 'REJECTED']:
        return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    report.status = status
    report.save()
    return Response({"message": f"Report {status.lower()} successfully."}, status=status.HTTP_200_OK)
