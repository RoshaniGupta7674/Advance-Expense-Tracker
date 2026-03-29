from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Dashboard & Landing
    path('', views.landing_or_dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about_page, name='about'),
    path('user-guide/', views.user_guide_page, name='user_guide'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # Auth
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.custom_forgot_password, name='custom_forgot_password'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),


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

    # Savings
    path('saving/', views.saving_list, name='saving_list'),
    path('saving/add/', views.add_saving, name='add_saving'),
    path('saving/edit/<int:id>/', views.edit_saving, name='edit_saving'),
    path('saving/delete/<int:id>/', views.delete_saving, name='delete_saving'),

    path("category/add/", views.add_category, name="add_category"),
    path("voice-expense/", views.voice_expense, name="voice_expense"),
    path("voice-income/", views.voice_income, name="voice_income"),
    path("voice-saving/", views.voice_saving, name="voice_saving"),
    path("voice-query/", views.voice_query, name="voice_query"),
    path("daily-summary/", views.daily_summary, name="daily_summary"),
    path("scan-receipt-page/", views.scan_receipt_view, name="scan_receipt_view"),
    path("scan-receipt/", views.scan_receipt, name="scan_receipt"),
    path("export-csv/", views.export_csv, name="export_csv"),

    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/delete/<int:id>/', views.delete_budget, name='delete_budget'),

    # Bills
    path('bills/', views.bills_list, name='bills_list'),
    path('bills/add/', views.add_bill, name='add_bill'),
    path('bills/toggle/<int:id>/', views.toggle_bill, name='toggle_bill'),
    path('bills/delete/<int:id>/', views.delete_bill, name='delete_bill'),
]