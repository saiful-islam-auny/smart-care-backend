from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Doctor

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Specialization
        fields = '__all__'
        
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Designation
        fields = '__all__'
        
class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AvailableTime
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)  
    designation = DesignationSerializer(many=True, read_only=True)  
    specialization = SpecializationSerializer(many=True, read_only=True)  
    available_time = AvailableTimeSerializer(many=True, read_only=True)  
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'first_name', 'last_name', 'image', 'image_url', 
            'designation', 'specialization', 'available_time', 'fee', 'meet_link', 
            'description', 'phone_number', 'email'
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

        
class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.user.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = models.Review
        fields = ['id', 'reviewer', 'reviewer_name', 'doctor', 'doctor_name', 'body', 'rating', 'created']


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Admin selects an existing user

    class Meta:
        model = Doctor
        fields = ['user', 'image', 'designation', 'specialization', 'available_time', 'fee', 'meet_link']

    def create(self, validated_data):
        return Doctor.objects.create(**validated_data)


class DoctorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            if hasattr(user, 'doctor'):  
                refresh = RefreshToken.for_user(user)
                return {
                    "email": user.email,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
            raise serializers.ValidationError("Only doctors can log in.")  # ✅ Fix: Block non-doctors
        raise serializers.ValidationError("Invalid credentials.")
