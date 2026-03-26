from django.contrib import admin
from .models import Category, Expense, Income

# Register your models here so they show up in the admin dashboard
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)