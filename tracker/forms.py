from django import forms
from .models import Expense ,Category 
from .models import Income


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


class IncomeForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = ['source','amount','date','note']

        widgets = {
            'date': forms.DateInput(attrs={'type':'date'})
        }
