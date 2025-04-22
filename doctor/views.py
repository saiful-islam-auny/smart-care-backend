from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from . import models
from . import serializers
from rest_framework import filters, pagination
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import DoctorLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveAPIView
from .serializers import DoctorSerializer, ReviewSerializer
from .models import Doctor
from rest_framework.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view


class SpecializationViewset(viewsets.ModelViewSet):
    queryset = models.Specialization.objects.all()
    serializer_class = serializers.SpecializationSerializer
    
    
class DesignationViewset(viewsets.ModelViewSet):
    queryset = models.Designation.objects.all()
    serializer_class = serializers.DesignationSerializer
    

class AvailableTimeForSpecificDoctor(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):  # Change query_set -> queryset
        doctor_id = request.query_params.get("doctor_id")
        if doctor_id:
            return queryset.filter(doctor=doctor_id)  # Change query_set -> queryset
        return queryset


class AvailableTimeViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.AvailableTime.objects.all()
    serializer_class = serializers.AvailableTimeSerializer
    filter_backends = [AvailableTimeForSpecificDoctor]

class DoctorPagination(pagination.PageNumberPagination):
    page_size = 5 # items per page
    page_size_query_param = "page_size"
    max_page_size = 100

class DoctorViewset(viewsets.ModelViewSet):
    queryset = models.Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = None  # ✅ Fix: Remove default pagination to handle dynamic limits
    search_fields = ['user__first_name', 'user__email', 'designation__name', 'specialization__name']
    permission_classes = [AllowAny]  
    http_method_names = ['get']

    def get_queryset(self):
        queryset = models.Doctor.objects.all()
        limit = self.request.query_params.get("limit")
        if limit:
            return queryset[:int(limit)]  # ✅ Fix: Apply dynamic limit
        return queryset


class ReviewViewset(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        doctor_id = self.request.query_params.get("doctor_id")
        if doctor_id:
            return models.Review.objects.filter(doctor_id=doctor_id)
        return models.Review.objects.all()

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'patient'):
            return Response({"error": "Only patients can submit reviews."}, status=status.HTTP_403_FORBIDDEN)

        reviewer = request.user.patient  # Now it's safe
        doctor_id = request.data.get('doctor')

        if models.Review.objects.filter(reviewer=reviewer, doctor_id=doctor_id).exists():
            return Response({"error": "You have already reviewed this doctor."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)



from rest_framework.permissions import IsAdminUser
from .serializers import DoctorRegistrationSerializer

class DoctorRegistrationView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can register doctors

    def post(self, request):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DoctorLoginView(APIView):
    def post(self, request):
        serializer = DoctorLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token

            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class DoctorProfileView(RetrieveAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            raise ValidationError("Doctor profile not found.")

        
    
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            raise ValidationError("Old password is incorrect.")

        user.set_password(new_password)
        user.save()

        # Optionally, create a new token after changing the password
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Password updated successfully.",
            "token": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a token for password reset
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:8000/doctor/password/reset/confirm/{user.pk}/{token}/"

        # Send reset link via email
        send_mail(
            'Password Reset Request',
            f'Please click the following link to reset your password: {reset_link}',
            'no-reply@hospital.com',
            [email]
        )

        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

# View to reset password
class PasswordResetConfirmView(APIView):
    def post(self, request, user_id, token):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"message": "Invalid user."}, status=status.HTTP_404_NOT_FOUND)

        if not default_token_generator.check_token(user, token):
            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    


@api_view(['GET'])
def doctor_list(request): 
    queryset = DoctorViewset().get_queryset()
    serializer = DoctorSerializer(queryset, many=True, context={"request": request})  # ✅ Fix: Add request context
    return Response(serializer.data)
