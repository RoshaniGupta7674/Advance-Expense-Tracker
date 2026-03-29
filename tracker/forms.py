from django import forms
from .models import Expense ,Category 
from .models import Income
from django.contrib.auth.models import User
from django.utils import timezone


class UserRegistrationForm(forms.ModelForm):
    security_question = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Security Question (e.g. Your first pet name?)'}), max_length=255, required=True)
    security_answer = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Security Answer'}), max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")
            
        # Also check if username exists natively, though ModelForm usually handles it.
        return cleaned_data


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'description','date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')   # 🔥 get logged-in user
        super().__init__(*args, **kwargs)

        # 🔥 filter categories per user
        self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("You cannot add future expenses.")
        return date


class IncomeForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = ['source','amount','date','note']

        widgets = {
            'date': forms.DateInput(attrs={'type':'date'})
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("You cannot add future incomes.")
        return date

class SavingForm(forms.ModelForm):
    class Meta:
        from .models import Saving
        model = Saving
        fields = ['source', 'amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError('You cannot add future savings.')
        return date

class BudgetForm(forms.ModelForm):
    class Meta:
        from .models import Budget
        model = Budget
        fields = ['category', 'limit', 'month']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.filter(user=user)

class BillReminderForm(forms.ModelForm):
    class Meta:
        from .models import BillReminder
        model = BillReminder
        fields = ['title', 'amount', 'due_date', 'is_recurring', 'is_paid']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

