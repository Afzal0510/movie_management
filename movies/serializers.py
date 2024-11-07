from django.contrib.auth import authenticate
from django.core.validators import MinValueValidator, MaxValueValidator
from knox.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import Movie, Rating, MovieReport
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers
from django.contrib.auth import authenticate

from rest_framework import serializers
from django.contrib.auth.models import User


class SignupApiSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validate the credentials and return the user if valid.
        """
        # Authenticate user with username and password
        user = authenticate(username=data['username'], password=data['password'])

        # If authentication fails, raise an error
        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        return {'user': user}


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'duration', 'genre', 'average_rating', 'total_rating', 'language', 'updated_at']
        read_only_fields = ['created_by', 'average_rating', 'total_rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Only update fields if the current user is the creator
        request_user = self.context['request'].user
        if instance.created_by != request_user:
            raise serializers.ValidationError("Only the creator can update this movie.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save without changing `updated_at` for rating changes only
        instance.save(update_fields=[field for field in validated_data.keys() if field != 'average_rating'])
        return instance



class RatingSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    class Meta:
        model = Rating
        fields = ['score']
        extra_kwargs = {
            'movie': {'required': True},  # Ensure movie is required
        }

class MovieReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieReport
        fields = ['movie','reason', 'status']
        read_only_fields = ['status']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
