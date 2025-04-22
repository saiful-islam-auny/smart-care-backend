from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import DoctorLoginView, DoctorLogoutView, DoctorProfileView, DoctorRegistrationView,PasswordChangeView, PasswordResetView, PasswordResetConfirmView,doctor_list
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('doctors', views.DoctorViewset)  # ✅ Fix: Change 'list' to 'doctors'
router.register('specialization', views.SpecializationViewset)
router.register('available_time', views.AvailableTimeViewset)
router.register('designation', views.DesignationViewset)
router.register('reviews', views.ReviewViewset, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', DoctorLoginView.as_view(), name='doctor_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', DoctorLogoutView.as_view(), name='doctor_logout'),
    path('profile/', DoctorProfileView.as_view(), name='doctor_profile'),
    path('register/', DoctorRegistrationView.as_view(), name='doctor_register'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<int:user_id>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
