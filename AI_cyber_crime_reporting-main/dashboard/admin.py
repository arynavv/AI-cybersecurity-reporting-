from django.contrib import admin
from .models import Case, Message # <-- Import your models

# Register your models here.
admin.site.register(Case)
admin.site.register(Message)