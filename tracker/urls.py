from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Auth
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Expense
    path('expense/', views.expense_list, name='expense_list'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:id>/', views.delete_expense, name='delete_expense'),

    # Income
    path('income/', views.income_list, name='income_list'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:id>/', views.delete_income, name='delete_income'),

    path("category/add/", views.add_category, name="add_category"),
    path("voice-expense/", views.voice_expense, name="voice_expense"),
    
]