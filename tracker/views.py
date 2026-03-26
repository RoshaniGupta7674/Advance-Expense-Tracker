import json, re, google.generativeai as genai
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from .models import Expense,Income,Category
from .forms import ExpenseForm,IncomeForm
from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


# @login_required
def dashboard(request):

    income_data = Income.objects.filter(user=request.user).aggregate(Sum('amount'))
    expense_data = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))

    total_income = income_data['amount__sum']
    total_expense = expense_data['amount__sum']

    # convert safely to Decimal
    if total_income is None:
        total_income = Decimal('0.00')
    else:
        total_income = Decimal(total_income)

    if total_expense is None:
        total_expense = Decimal('0.00')
    else:
        total_expense = Decimal(total_expense)

    balance = total_income - total_expense

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }

    return render(request, "dashboard.html", context)
# @login_required
# def dashboard(request):

#     income_total = Income.objects.filter(user=request.user)
#     expense_total = Expense.objects.filter(user=request.user)

#     total_income = sum(i.amount for i in income_total)
#     total_expense = sum(e.amount for e in expense_total)

#     balance = total_income - total_expense

#     context = {

#         "income": total_income,
#         "expense": total_expense,
#         "balance": balance

#     }

#     return render(request,"dashboard.html",context)

# Income Module

@login_required
def add_income(request):

    if request.method == "POST":

        form = IncomeForm(request.POST)

        if form.is_valid():

            income = form.save(commit=False)
            income.user = request.user
            income.save()

            return redirect('/income/')

    else:
        form = IncomeForm()

    return render(request,'add_income.html',{'form':form})


# @login_required
def income_list(request):

    incomes = Income.objects.filter(user=request.user).order_by('-date')

    return render(request,'income_list.html',{'incomes':incomes})


# EDIT EXPENSE
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "edit_expense.html", {"form": form})


# DELETE EXPENSE
@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect("expense_list")


# EDIT INCOME
@login_required
def edit_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)

    if request.method == "POST":
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect("income_list")
    else:
        form = IncomeForm(instance=income)

    return render(request, "edit_income.html", {"form": form})


# DELETE INCOME
@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    income.delete()
    return redirect("income_list")

# Expense Module
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request,'expense.html',{'expenses':expenses})

# @login_required
# def add_expense(request):

#     form = ExpenseForm(request.POST or None)

#     if form.is_valid():

#         expense = form.save(commit=False)

#         if request.user.is_authenticated:
#             expense.user = request.user

#         expense.save()

#         return redirect('/expense')

#     return render(request,'add_expense.html',{'form':form})
# ___________________________________________________________________
# @login_required
# def add_expense(request):
#     if request.method == "POST":
#         amount = request.POST['amount']
#         category_id = request.POST['category']
#         description = request.POST['description']

#         category = Category.objects.get(id=category_id)

#         Expense.objects.create(
#             user=request.user,
#             amount=amount,
#             category=category,
#             description=description
#         )
#         return redirect('expense')

#     categories = Category.objects.filter(user=request.user)

#     return render(request, 'add_expense.html', {'categories': categories})

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)

    return render(request, 'add_expense.html', {'form': form})

def add_category(request):
    if request.method == "POST":
        name = request.POST['name']

        Category.objects.create(
            user=request.user,
            name=name
        )
        return redirect('add_expense')

    return render(request, 'add_category.html')

# @login_required
# def edit_expense(request,id):

#     expense = get_object_or_404(Expense,id=id)

#     form = ExpenseForm(request.POST or None,instance=expense)

#     if form.is_valid():

#         form.save()

#         return redirect('/expense')

#     return render(request,'add_expense.html',{'form':form})

@login_required
def edit_expense(request, id):
    expense = Expense.objects.get(id=id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('expense_list')   # or your correct URL name
    else:
        form = ExpenseForm(instance=expense, user=request.user)

    return render(request, 'edit_expense.html', {'form': form})

@login_required
def delete_expense(request,id):

    expense = get_object_or_404(Expense,id=id)

    expense.delete()

    return redirect('/expense')

# login

def user_login(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request,"login.html",{"error":"Invalid credentials"})

    return render(request,"login.html")


# register

def register(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(username=username,email=email,password=password)

        return redirect("/login/")

    return render(request,"register.html")


def user_logout(request):

    logout(request)
    return redirect('/login')


# 1. MAKE SURE THIS KEY IS VALID. Get one at: https://aistudio.google.com/
genai.configure(api_key="AIzaSyAy24BLv5SL5vA98iZ9wWp7Wi2RgSdp2v8")

@csrf_exempt
def voice_expense(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "")

            # ... (Your Gemini AI parsing logic here) ...

            # FIX: Use .filter().first() to avoid "returned more than one" error
            category_name = extracted.get("category", "Other").strip().title()
            category = Category.objects.filter(name=category_name, user=request.user).first()

            if not category:
                category = Category.objects.create(name=category_name, user=request.user)

            # SAVE: Create the expense
            Expense.objects.create(
                user=request.user,
                amount=extracted.get("amount", 0),
                category=category,
                description=extracted.get("description", user_text),
                date=extracted.get("date", timezone.now().date())
            )

            return JsonResponse({"status": "success", "message": f"✅ Saved ₹{extracted.get('amount')}"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})