from django.db import models
from django.contrib.auth.models import User
from patient.models import Patient
from django.core.validators import RegexValidator

# Create your models here.

class Specialization(models.Model):
    name = models.CharField(max_length = 30)
    slug = models.SlugField(max_length = 40)
    def __str__(self):
        return self.name
class Designation(models.Model):
    name = models.CharField(max_length = 30)
    slug = models.SlugField(max_length = 40)
    def __str__(self):
            return self.name
class AvailableTime(models.Model):
    name = models.CharField(max_length = 100)
    
    def __str__(self):
        return self.name


# one to many --> many part e kintu foreign key add kortam
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="doctor/images/")
    designation = models.ManyToManyField(Designation)
    specialization = models.ManyToManyField(Specialization)
    available_time = models.ManyToManyField(AvailableTime)
    fee = models.IntegerField()
    meet_link = models.URLField(max_length=200)
    description = models.TextField(blank=True, null=True)  # 🔹 Doctor's bio/description
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{9,15}$', "Enter a valid phone number.")],
        unique=True
    )  # 🔹 Ensuring valid phone number format

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_email(self):
        return self.user.email  # 🔹 Returns doctor's email

class Review(models.Model):
    reviewer = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="reviews")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=[(i, '⭐' * i) for i in range(1, 6)])  # 🔹 Store ratings as numbers

    def __str__(self):
        return f"Patient: {self.reviewer.user.first_name} | Doctor: {self.doctor.user.first_name} | Rating: {self.rating}"
