from django.contrib import admin
from . import models  # Import all models

# Fix: Remove duplicate registration for Doctor
admin.site.register(models.AvailableTime)

class SpecializationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class DesignationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "get_email", "phone_number", "fee", "meet_link")

    def get_email(self, obj):
        return obj.user.email  # Access the related user's email

    get_email.short_description = "Email"

# Register the Doctor model only once
admin.site.register(models.Doctor, DoctorAdmin)
admin.site.register(models.Specialization, SpecializationAdmin)
admin.site.register(models.Designation, DesignationAdmin)
admin.site.register(models.Review)
