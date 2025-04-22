from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Patient
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Properly serialize user fields

    class Meta:
        model = Patient
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    mobile_no = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'mobile_no']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'error': "Passwords do not match"})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'error': "Email already exists"})
        if Patient.objects.filter(mobile_no=attrs['mobile_no']).exists():
            raise serializers.ValidationError({'error': "Mobile number already exists"})
        return attrs

    def create(self, validated_data):
        mobile_no = validated_data.pop('mobile_no')
        validated_data.pop('confirm_password')  
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        user.is_active = False  
        user.save()

        Patient.objects.create(user=user, mobile_no=mobile_no)

        refresh = RefreshToken.for_user(user)
        return {
            'user_id': user.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': "Check your email to activate your account"
        }


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()
        if user:
            if not user.is_active:  # 🔹 Prevent login if user is not activated
                raise serializers.ValidationError({'error': "Your account is not activated. Check your email."})
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return {
                    'user_id': user.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
        
        raise serializers.ValidationError({'error': "Invalid credentials"})
