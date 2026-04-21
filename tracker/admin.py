from django.contrib import admin
from .models import Category, Expense, Income, Saving, UserProfile,Budget , BillReminder

# Register your models here so they show up in the admin dashboard
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Saving)
admin.site.register(UserProfile)
admin.site.register(Budget)
admin.site.register(BillReminder)