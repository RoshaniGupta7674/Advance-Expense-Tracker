from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Expense(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    description = models.TextField(blank=True)

    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.category} - {self.amount}"
    

class Income(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    source = models.CharField(max_length=200)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    date = models.DateField()

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source

class Saving(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=200, help_text="Where this saving came from or its purpose")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)
    plain_password = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} Budget"

class BillReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} due {self.due_date}"