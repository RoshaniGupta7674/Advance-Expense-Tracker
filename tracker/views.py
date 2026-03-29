import json, re, google.generativeai as genai
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from .models import Expense,Income,Category,Budget,BillReminder,Saving,UserProfile
from .forms import ExpenseForm, IncomeForm, UserRegistrationForm, SavingForm, BudgetForm, BillReminderForm
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def check_expense_limit(user, request):
    income_data = Income.objects.filter(user=user).aggregate(Sum('amount'))
    expense_data = Expense.objects.filter(user=user).aggregate(Sum('amount'))
    total_income = income_data['amount__sum'] or Decimal('0.00')
    total_expense = expense_data['amount__sum'] or Decimal('0.00')
    if total_income > 0 and total_expense > Decimal('0.8') * total_income:
        messages.warning(request, "⚠️ Alert: Your expenses have exceeded 80% of your total income!")
        
    current_month_start = timezone.now().replace(day=1)
    budgets = Budget.objects.filter(user=user)
    for budget in budgets:
        cat_expense = Expense.objects.filter(
            user=user, 
            category=budget.category, 
            date__gte=current_month_start.date()
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        if budget.limit > 0 and cat_expense >= Decimal('0.8') * budget.limit:
            percentage = int((cat_expense / budget.limit) * 100)
            messages.warning(request, f"🚨 Alert: You have spent {percentage}% of your monthly {budget.category.name} budget.")


@login_required
def dashboard(request):
    income_data = Income.objects.filter(user=request.user).aggregate(Sum('amount'))
    expense_data = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))
    saving_data = Saving.objects.filter(user=request.user).aggregate(Sum('amount'))

    total_income = income_data['amount__sum'] or Decimal('0.00')
    total_expense = expense_data['amount__sum'] or Decimal('0.00')
    total_saving = saving_data['amount__sum'] or Decimal('0.00')
    balance = (total_income - total_expense - total_saving)
    
    # recent transactions
    recent_incomes = list(Income.objects.filter(user=request.user).order_by('-date')[:5])
    recent_expenses = list(Expense.objects.filter(user=request.user).order_by('-date')[:5])
    recent_savings = list(Saving.objects.filter(user=request.user).order_by('-date')[:5])
    
    for r in recent_incomes:
        r.type_label = 'Income'
        r.display_title = getattr(r, 'source', 'Income')
    for r in recent_expenses:
        r.type_label = 'Expense'
        r.display_title = r.category.name if getattr(r, 'category', None) else 'Expense'
    for r in recent_savings:
        r.type_label = 'Saving'
        r.display_title = getattr(r, 'source', 'Saving')
        
    all_recent = recent_incomes + recent_expenses + recent_savings
    all_recent.sort(key=lambda x: getattr(x, 'date'), reverse=True)
    all_recent = all_recent[:5]

    check_expense_limit(request.user, request)
    
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    upcoming_bills = BillReminder.objects.filter(user=request.user, is_paid=False, due_date__lte=tomorrow)
    for bill in upcoming_bills:
        if bill.due_date == tomorrow:
            messages.warning(request, f"Reminder: Your bill '{bill.title}' for ₹{bill.amount} is due tomorrow!")
        elif bill.due_date <= today:
            messages.error(request, f"Alert: Your bill '{bill.title}' for ₹{bill.amount} is overdue!")

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_saving": total_saving,
        "balance": balance,
        
        "recent_transactions": all_recent,
    }

    return render(request, "dashboard.html", context)

@login_required
def reports(request):
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()
    
    # Base querysets
    expense_qs = Expense.objects.filter(user=request.user)
    income_qs = Income.objects.filter(user=request.user)

    # Apply filter
    if filter_type == 'last_7_days':
        start_date = today - timedelta(days=7)
        expense_qs = expense_qs.filter(date__gte=start_date)
        income_qs = income_qs.filter(date__gte=start_date)
    elif filter_type == 'this_month':
        start_date = today.replace(day=1)
        expense_qs = expense_qs.filter(date__gte=start_date)
        income_qs = income_qs.filter(date__gte=start_date)
    elif filter_type == 'this_year':
        start_date = today.replace(month=1, day=1)
        expense_qs = expense_qs.filter(date__gte=start_date)
        income_qs = income_qs.filter(date__gte=start_date)

    # Mini KPIs
    total_expense = expense_qs.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_income = income_qs.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Chart Data: Expenses by Category
    expenses_by_cat = expense_qs.values('category__name').annotate(total=Sum('amount'))
    expense_labels = [e['category__name'] for e in expenses_by_cat]
    expense_values = [float(e['total']) for e in expenses_by_cat]

    # Chart Data: Income by Source
    incomes_by_src = income_qs.values('source').annotate(total=Sum('amount'))
    income_labels = [i['source'] for i in incomes_by_src]
    income_values = [float(i['total']) for i in incomes_by_src]

    # Expense Prediction: Better averaging
    first_expense = Expense.objects.filter(user=request.user).order_by('date').first()
    if first_expense:
        days_active = (today - first_expense.date).days or 1
        total_all_time = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        daily_avg = total_all_time / Decimal(str(days_active))
        predicted_next_month = round(daily_avg * Decimal('30.0') * Decimal('1.05'), 2)
    else:
        predicted_next_month = Decimal('0.00')

    # Chart Data: Expense Trend (Line Chart by Date)
    trend_data = expense_qs.values('date').annotate(total=Sum('amount')).order_by('date')
    trend_labels = [t['date'].strftime('%Y-%m-%d') for t in trend_data]
    trend_values = [float(t['total']) for t in trend_data]

    # Recent Transactions
    recent_expenses = expense_qs.order_by('-date')[:5]
    recent_incomes = income_qs.order_by('-date')[:5]

    context = {
        "current_filter": filter_type,
        "total_expense": total_expense,
        "total_income": total_income,
        "expense_labels": json.dumps(expense_labels),
        "expense_values": json.dumps(expense_values),
        "income_labels": json.dumps(income_labels),
        "income_values": json.dumps(income_values),
        "trend_labels": json.dumps(trend_labels),
        "trend_values": json.dumps(trend_values),
        "recent_expenses": recent_expenses,
        "recent_incomes": recent_incomes,
        "predicted_next_month": predicted_next_month,
    }

    return render(request, "reports.html", context)
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
            messages.success(request, "Income added successfully.")
            return redirect('/income/')
    else:
        form = IncomeForm()

    return render(request,'add_income.html',{'form':form})


@login_required
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
            
            # --- Check if expense exceeds income ---
            income_total = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            expense_total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            if expense_total + expense.amount > income_total:
                messages.error(request, "Error: Adding this expense would exceed your total income. Transaction denied.")
                return render(request, 'add_expense.html', {'form': form})
                
            expense.user = request.user
            expense.save()
            check_expense_limit(request.user, request)
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
            updated_expense = form.save(commit=False)
            
            income_total = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            expense_total = Expense.objects.filter(user=request.user).exclude(id=updated_expense.id).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            if expense_total + updated_expense.amount > income_total:
                messages.error(request, "Error: Updating this expense would exceed your total income. Transaction denied.")
                return render(request, 'edit_expense.html', {'form': form})
                
            updated_expense.save()
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

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request,"login.html")

    return render(request,"login.html")


# register

def register(request):

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                security_question=form.cleaned_data.get('security_question', ''),
                security_answer=form.cleaned_data.get('security_answer', ''),
                plain_password=form.cleaned_data.get('password', '')
            )
            messages.success(request, "Registration successful. Please login.")
            return redirect("/login/")
    else:
        form = UserRegistrationForm()

    return render(request,"register.html", {'form': form})


def user_logout(request):
    logout(request)
    return redirect('/login')

def custom_forgot_password(request):
    if request.method == "POST":
        identifier = request.POST.get('identifier', '')
        answer = request.POST.get('answer', '')
        
        # Step 1: Lookup user
        if 'step' in request.POST and request.POST.get('step') == '1':
            user = User.objects.filter(username=identifier).first()
            if not user:
                user = User.objects.filter(email=identifier).first()
            
            if user:
                from .models import UserProfile
                try:
                    profile = user.userprofile
                    return render(request, "custom_forgot_password.html", {
                        "step": "2",
                        "identifier": identifier,
                        "question": profile.security_question
                    })
                except UserProfile.DoesNotExist:
                    messages.error(request, "This account does not have a security question set up.")
            else:
                messages.error(request, "User not found.")
                
        # Step 2: Verify answer
        elif 'step' in request.POST and request.POST.get('step') == '2':
            user = User.objects.filter(username=identifier).first()
            if not user:
                user = User.objects.filter(email=identifier).first()
                
            if user:
                from .models import UserProfile
                try:
                    profile = user.userprofile
                    if profile.security_answer.lower() == answer.lower().strip():
                        return render(request, "custom_forgot_password.html", {
                            "step": "3",
                            "plain_password": profile.plain_password
                        })
                    else:
                        messages.error(request, "Incorrect answer to security question.")
                        return render(request, "custom_forgot_password.html", {
                            "step": "2",
                            "identifier": identifier,
                            "question": profile.security_question
                        })
                except UserProfile.DoesNotExist:
                    pass
        
    return render(request, "custom_forgot_password.html", {"step": "1"})

def _deprecated_user_logout_placeholder(request):

    logout(request)
    return redirect('/login')


# 1. MAKE SURE THIS KEY IS VALID. Get one at: https://aistudio.google.com/
genai.configure(api_key="AIzaSyAy24BLv5SL5vA98iZ9wWp7Wi2RgSdp2v8")

def text_to_digit(text):
    """Converts words like 'two hundred' or '5k' into integers."""
    text = text.lower().replace("-", " ")
    
    # Handle 'k' notation (e.g., 2k -> 2000)
    k_match = re.search(r'(\d+)\s*k', text)
    if k_match:
        return int(k_match.group(1)) * 1000

    # Simple word map for common expense amounts
    word_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'hundred': 100, 'thousand': 1000, 'lakh': 100000
    }
    
    # Extract digits first
    digit_match = re.search(r'(\d+)', text)
    if digit_match:
        return int(digit_match.group(1))

    # Fallback: Check for words if no digits found
    total = 0
    words = text.split()
    for i, word in enumerate(words):
        if word in word_map:
            val = word_map[word]
            if val >= 100 and i > 0 and words[i-1] in word_map:
                total = (total + word_map[words[i-1]]) * val
            else:
                total += val
    return total if total > 0 else None

@csrf_exempt
def voice_expense(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").lower()
            
            # --- 1. AI PARSING ---
            extracted_cat = "Other"
            extracted_amt = 0
            
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                # Strict prompt to force category detection
                prompt = f"""
                Analyze: "{user_text}"
                1. Identify the 'amount' as an integer.
                2. Identify the 'category' based on the context (e.g., Food, Shopping, Transport, Rent, Bills). 
                If the user mentions "shopping", the category MUST be "Shopping".
                If the user mentions stores or items like "Domino's", "McDonald's", "Pizza", "restaurant", it MUST be "Food".
                Use your general knowledge to smartly map the mentioned item/store to the most logical category.
                Return ONLY JSON: {{"amount": int, "category": "string"}}
                """
                response = model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    ai_data = json.loads(match.group())
                    extracted_amt = ai_data.get("amount", 0)
                    extracted_cat = ai_data.get("category", "Other")
            except Exception as e:
                print(f"AI Logic Error: {e}")

            # --- 2. KEYWORD FALLBACK (Safety Net) ---
            # If AI fails or returns "Other", we manually check for common keywords
            if extracted_cat.lower() == "other":
                keywords = {
                    "shopping": "Shopping",
                    "food": "Food",
                    "eat": "Food",
                    "dinner": "Food",
                    "lunch": "Food",
                    "petrol": "Fuel",
                    "fuel": "Fuel",
                    "rent": "Rent",
                    "recharge": "Bills",
                    "bill": "Bills",
                    "medicine": "Health",
                    "doctor": "Health"
                }
                for word, cat in keywords.items():
                    if word in user_text:
                        extracted_cat = cat
                        break

            # Manual amount backup if AI missed it
            if not extracted_amt:
                amt_match = re.search(r'(\d+)', user_text)
                extracted_amt = int(amt_match.group(1)) if amt_match else 0

            # --- 3. DATABASE SAVE ---
            if extracted_amt > 0:
                cat_name = extracted_cat.strip().title()
                
                income_total = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
                expense_total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
                
                if float(expense_total) + float(extracted_amt) > float(income_total):
                    return JsonResponse({"status": "error", "message": "Error: Expense exceeds total income. Transaction denied."})
                
                # Use iexact to find "Food" even if stored as "food"
                category = Category.objects.filter(name__iexact=cat_name, user=request.user).first()
                
                if not category:
                    category = Category.objects.create(name=cat_name, user=request.user)

                Expense.objects.create(
                    user=request.user,
                    amount=extracted_amt,
                    category=category,
                    description=user_text,
                    date=timezone.now().date()
                )
                return JsonResponse({"status": "success", "message": f"✅ Added ₹{extracted_amt} for {cat_name}"})
            
            return JsonResponse({"status": "error", "message": "No amount detected."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def voice_income(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").lower()
            
            # --- 1. AI PARSING ---
            extracted_source = "Other"
            extracted_amt = 0
            
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                # Strict prompt to force source detection
                prompt = f"""
                Analyze: "{user_text}"
                1. Identify the 'amount' as an integer.
                2. Identify the 'source' of income based on the context (e.g., Salary, Freelance, Business, Gift, Bonus). 
                If the user mentions "salary", the source MUST be "Salary".
                Return ONLY JSON: {{"amount": int, "source": "string"}}
                """
                response = model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    ai_data = json.loads(match.group())
                    extracted_amt = ai_data.get("amount", 0)
                    extracted_source = ai_data.get("source", "Other")
            except Exception as e:
                print(f"AI Logic Error: {e}")

            # --- 2. KEYWORD FALLBACK (Safety Net) ---
            if extracted_source.lower() == "other":
                keywords = {
                    "salary": "Salary",
                    "freelance": "Freelance",
                    "business": "Business",
                    "gift": "Gift",
                    "bonus": "Bonus",
                    "dividend": "Dividend",
                    "rent": "Rental Income",
                    "interest": "Interest",
                    "sold": "Sales"
                }
                for word, source in keywords.items():
                    if word in user_text:
                        extracted_source = source
                        break

            # Manual amount backup if AI missed it
            if not extracted_amt:
                amt_match = re.search(r'(\d+)', user_text)
                extracted_amt = int(amt_match.group(1)) if amt_match else 0

            # --- 3. DATABASE SAVE ---
            if extracted_amt > 0:
                source_name = extracted_source.strip().title()
                
                Income.objects.create(
                    user=request.user,
                    amount=extracted_amt,
                    source=source_name,
                    note=user_text,
                    date=timezone.now().date()
                )
                return JsonResponse({"status": "success", "message": f"✅ Added ₹{extracted_amt} from {source_name}"})
            
            return JsonResponse({"status": "error", "message": "No amount detected."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def voice_query(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Please login to ask questions."})
            
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").lower()
            
            # Aggregate stats
            current_month_start = timezone.now().replace(day=1)
            expenses = Expense.objects.filter(user=request.user, date__gte=current_month_start)
            total_spent = sum(e.amount for e in expenses)
            
            context_data = f"Total spent this month: {total_spent}."
            cat_totals = {}
            for e in expenses:
                cat_totals[e.category.name] = cat_totals.get(e.category.name, 0) + e.amount
            
            context_data += " Category breakdown: " + ", ".join([f"{k}: {v}" for k, v in cat_totals.items()])
                
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            prompt = f"""
            You are a helpful AI financial assistant. Provide a brief, natural language answer to the user query.
            User Query: "{user_text}"
            Context Data (This month's expenses): {context_data}
            Do NOT use markdown. Keep the response under 15 words. Example constraint: "You have spent 4000 on food this month."
            """
            response = model.generate_content(prompt)
            # Remove any asterisks that might slip in
            clean_text = response.text.strip().replace("*", "")
            return JsonResponse({"status": "success", "message": clean_text})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

@login_required
def daily_summary(request):
    today = timezone.now().date()
    
    # Expenses
    expenses = Expense.objects.filter(user=request.user, date=today)
    total_spent = sum(e.amount for e in expenses)
    expense_count = expenses.count()
    
    # Incomes
    incomes = Income.objects.filter(user=request.user, date=today)
    total_earned = sum(i.amount for i in incomes)
    
    # Balance
    balance = total_earned - total_spent
    
    if expense_count == 0 and total_earned == 0:
        msg = "You have no expenses or income recorded for today. Great job keeping a low profile!"
    else:
        msg = f"Today's Summary: You earned {total_earned} and spent {total_spent} in {expense_count} transactions. Your net balance for the day is {balance} rupees."
        if total_spent > total_earned:
            msg += " Be careful, you spent more than you earned today!"
        
    return JsonResponse({"status": "success", "message": msg})

import tempfile
import atexit
import os
from PIL import Image

@csrf_exempt
def scan_receipt(request):
    if request.method == "POST":
        if "receipt" not in request.FILES:
            return JsonResponse({"status": "error", "message": "No image uploaded."})
            
        try:
            image_file = request.FILES["receipt"]
            img = Image.open(image_file)
            
            prompt = """
            Analyze this receipt image. Extract the following information:
            1. Total amount (just the number).
            2. Best matching expense Category (e.g., Food, Shopping, Transport, Bills).
            3. A short description string including the Shop/Store name.
            Return ONLY a valid JSON format like: {"amount": float, "category": "String", "description": "Shop Name - Items"}
            """
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content([prompt, img])
            
            # extract JSON
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                
                amount_str = str(data.get("amount", "0")).replace(',', '')
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0
                    
                cat_name = data.get("category", "Other").strip().title()
                desc = data.get("description", "Receipt Scan")
                
                if not request.user.is_authenticated:
                     return JsonResponse({"status": "error", "message": "User not authenticated."})
                     
                category = Category.objects.filter(name__iexact=cat_name, user=request.user).first()
                if not category:
                    category = Category.objects.create(name=cat_name, user=request.user)
                    
                income_total = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
                expense_total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
                
                if float(expense_total) + float(amount) > float(income_total):
                    return JsonResponse({"status": "error", "message": "Error: Scanned expense exceeds total income. Transaction denied."})

                exp = Expense.objects.create(
                    user=request.user,
                    amount=amount,
                    category=category,
                    description=desc,
                    date=timezone.now().date()
                )
                
                return JsonResponse({"status": "success", "data": {
                    "amount": amount,
                    "category": cat_name,
                    "description": desc,
                    "date": str(exp.date)
                }})
            return JsonResponse({"status": "error", "message": "AI could not parse data from the image."})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

@login_required
def scan_receipt_view(request):
    return render(request, "scan_receipt.html")


import csv
from django.http import HttpResponse

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unified_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Title', 'Description', 'Amount'])

    expenses = list(Expense.objects.filter(user=request.user))
    incomes = list(Income.objects.filter(user=request.user))
    savings = list(Saving.objects.filter(user=request.user))
    
    for e in expenses:
        e.report_type = "Expense"
        e.report_title = e.category.name if getattr(e, 'category', None) else ""
        e.report_desc = e.description
    for i in incomes:
        i.report_type = "Income"
        i.report_title = i.source
        i.report_desc = i.note
    for s in savings:
        s.report_type = "Saving"
        s.report_title = s.source
        s.report_desc = s.note
        
    all_records = expenses + incomes + savings
    all_records.sort(key=lambda x: getattr(x, 'date', None) or timezone.now().date(), reverse=True)
    
    total_inc = Decimal('0.00')
    total_exp = Decimal('0.00')
    total_sav = Decimal('0.00')
    
    for r in all_records:
        r_amount = getattr(r, 'amount', Decimal('0.00'))
        writer.writerow([getattr(r, 'date', ''), r.report_type, r.report_title, r.report_desc, r_amount])
        if r.report_type == 'Expense':
            total_exp += r_amount
        elif r.report_type == 'Income':
            total_inc += r_amount
        else:
            total_sav += r_amount
            
    writer.writerow([])
    writer.writerow(['', '', '', 'Total Income:', total_inc])
    writer.writerow(['', '', '', 'Total Expense:', total_exp])
    writer.writerow(['', '', '', 'Total Savings:', total_sav])
    writer.writerow(['', '', '', 'Net Balance:', total_inc - total_exp - total_sav])

    return response

# ====== SAVING MODULE ======
@login_required
def saving_list(request):
    savings = Saving.objects.filter(user=request.user).order_by('-date')
    return render(request, 'saving_list.html', {'savings': savings})

@login_required
def add_saving(request):
    if request.method == "POST":
        form = SavingForm(request.POST)
        if form.is_valid():
            saving = form.save(commit=False)
            saving.user = request.user
            saving.save()
            messages.success(request, "Saving added successfully.")
            return redirect('saving_list')
    else:
        form = SavingForm()
    return render(request, 'add_saving.html', {'form': form})

@login_required
def edit_saving(request, id):
    saving = get_object_or_404(Saving, id=id, user=request.user)
    if request.method == "POST":
        form = SavingForm(request.POST, instance=saving)
        if form.is_valid():
            form.save()
            return redirect("saving_list")
    else:
        form = SavingForm(instance=saving)
    return render(request, "edit_saving.html", {"form": form})

@login_required
def delete_saving(request, id):
    saving = get_object_or_404(Saving, id=id, user=request.user)
    saving.delete()
    return redirect("saving_list")

@csrf_exempt
def voice_saving(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").lower()
            
            extracted_source = "Other"
            extracted_amt = 0
            
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                prompt = f"""
                Analyze: "{user_text}"
                1. Identify the 'amount' as an integer.
                2. Identify the 'source' or 'goal' of the saving based on the context.
                Return ONLY JSON: {{"amount": int, "source": "string"}}
                """
                response = model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    ai_data = json.loads(match.group())
                    extracted_amt = ai_data.get("amount", 0)
                    extracted_source = ai_data.get("source", "Other")
            except Exception as e:
                print(f"AI Logic Error: {e}")

            if not extracted_amt:
                amt_match = re.search(r'(\d+)', user_text)
                extracted_amt = int(amt_match.group(1)) if amt_match else 0

            if extracted_amt > 0:
                source_name = extracted_source.strip().title()
                
                Saving.objects.create(
                    user=request.user,
                    amount=extracted_amt,
                    source=source_name,
                    note=user_text,
                    date=timezone.now().date()
                )
                return JsonResponse({"status": "success", "message": f"✅ Saved ₹{extracted_amt} for {source_name}"})
            
            return JsonResponse({"status": "error", "message": "No amount detected."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

def landing_or_dashboard(request):
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, "landing.html")

def about_page(request):
    return render(request, "about.html")

def user_guide_page(request):
    return render(request, "user_guide.html")

# ====== BUDGET MODULE ======
@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    current_month_start = timezone.now().replace(day=1)
    
    for budget in budgets:
        spent = Expense.objects.filter(
            user=request.user, 
            category=budget.category,
            date__gte=current_month_start.date()
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        budget.spent = float(spent)
        budget.percentage = min(int((budget.spent / float(budget.limit)) * 100), 100) if budget.limit > 0 else 0
        budget.is_over_limit = budget.spent > budget.limit

    return render(request, 'budget_list.html', {'budgets': budgets})

@login_required
def add_budget(request):
    if request.method == "POST":
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    return render(request, 'add_budget.html', {'form': form})

@login_required
def delete_budget(request, id):
    budget = get_object_or_404(Budget, id=id, user=request.user)
    budget.delete()
    return redirect('budget_list')

# ====== BILLS MODULE ======
@login_required
def bills_list(request):
    bills = BillReminder.objects.filter(user=request.user).order_by('due_date')
    return render(request, 'bills.html', {'bills': bills})

@login_required
def add_bill(request):
    if request.method == "POST":
        form = BillReminderForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            return redirect('bills_list')
    else:
        form = BillReminderForm()
    return render(request, 'add_bill.html', {'form': form})

@login_required
def toggle_bill(request, id):
    bill = get_object_or_404(BillReminder, id=id, user=request.user)
    
    if not bill.is_paid:
        bill.is_paid = True
        if bill.is_recurring:
            import calendar
            days_in_month = calendar.monthrange(bill.due_date.year, bill.due_date.month)[1]
            bill.due_date = bill.due_date + timedelta(days=days_in_month)
            bill.is_paid = False
    else:
        bill.is_paid = False
        
    bill.save()
    return redirect('bills_list')

@login_required
def delete_bill(request, id):
    bill = get_object_or_404(BillReminder, id=id, user=request.user)
    bill.delete()
    return redirect('bills_list')
