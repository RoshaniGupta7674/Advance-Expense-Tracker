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