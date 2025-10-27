from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (Deal, Inspection, Message, Notification, Property,
                     PropertyImage, Review, SavedProperty, UserProfile)
from .serializers import (DealSerializer, InspectionSerializer,
                          LoginSerializer, LogoutSerializer, MessageSerializer,
                          NotificationSerializer, PropertyImageSerializer,
                          PropertySerializer, RegisterSerializer,
                          ReviewSerializer, SavedPropertySerializer,
                          UserProfileSerializer, UserSerializer)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Logout successful."}, status=status.HTTP_204_NO_CONTENT)

class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'verification_status', 'is_verified']
    search_fields = ['user__username', 'user__email', 'bio']

    def get_queryset(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return UserProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'city', 'state', 'status', 'is_verified', 'is_furnished', 'has_parking', 'pets_allowed']
    search_fields = ['title', 'description', 'address', 'landmark']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        property = self.get_object()
        property.views_count += 1
        property.save()
        return Response({'views_count': property.views_count})

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyImage.objects.filter(property__owner=self.request.user)

class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'property', 'agent', 'preferred_date']

    def get_queryset(self):
        user = self.request.user
        return Inspection.objects.filter(
            models.Q(requester=user) | 
            models.Q(agent=user) | 
            models.Q(property__owner=user)
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        inspection = self.get_object()
        user = request.user
        
        if user == inspection.property.owner:
            inspection.confirmed_by_tenant = True
        elif user == inspection.agent:
            inspection.confirmed_by_agent = True
        
        if inspection.confirmed_by_tenant and inspection.confirmed_by_agent:
            inspection.status = Inspection.Status.CONFIRMED
        
        inspection.save()
        return Response(InspectionSerializer(inspection).data)

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'property', 'tenant', 'owner', 'agent']

    def get_queryset(self):
        user = self.request.user
        return Deal.objects.filter(
            models.Q(tenant=user) | 
            models.Q(owner=user) | 
            models.Q(agent=user)
        )

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_type', 'property', 'reviewed_user', 'is_verified_stay']

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        review = self.get_object()
        review.is_flagged = True
        review.flag_reason = request.data.get('reason', '')
        review.save()
        return Response({'status': 'review flagged'})

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | 
            models.Q(recipient=user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient == request.user and not message.is_read:
            message.is_read = True
            message.save()
        return Response({'status': 'message marked as read'})

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

class SavedPropertyViewSet(viewsets.ModelViewSet):
    queryset = SavedProperty.objects.all()
    serializer_class = SavedPropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
