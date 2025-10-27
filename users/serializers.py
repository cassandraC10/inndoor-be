from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import (Deal, Inspection, Message, Notification, Property,
                     PropertyImage, Review, SavedProperty, UserProfile)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['total_listings', 'total_inspections', 'rating']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['views_count', 'is_verified', 'verified_at', 'verified_by']


class InspectionSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    agent = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Inspection
        fields = '__all__'


class DealSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    agent = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Deal
        fields = '__all__'
        read_only_fields = ['paid_at']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    reviewed_user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['is_flagged', 'flag_reason']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['is_read', 'read_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['is_read', 'read_at']


class SavedPropertySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = SavedProperty
        fields = '__all__'