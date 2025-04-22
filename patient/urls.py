from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PatientViewset, UserRegistrationApiView, UserLoginApiView, UserLogoutView, activate,PatientProfileView,PatientListView

router = DefaultRouter() # our router

router.register('list', PatientViewset) # router antena
urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationApiView.as_view(), name='register'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('activate/<uid64>/<token>/', activate, name='activate'),
    path('profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('all/', PatientListView.as_view(), name='all-patients'),
]