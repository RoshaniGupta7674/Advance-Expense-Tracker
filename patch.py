import re

with open("tracker/views.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "from .models import Expense,Income,Category,Budget,BillReminder,FamilyGroup",
    "from .models import Expense,Income,Category,Budget,BillReminder,FamilyGroup,Saving"
)
content = content.replace(
    "from .forms import ExpenseForm,IncomeForm, UserRegistrationForm",
    "from .forms import ExpenseForm,IncomeForm, UserRegistrationForm, SavingForm"
)

# 2. Dashboard
dash_target = """@login_required
def dashboard(request):
    view_type = request.GET.get('view', 'personal')
    
    if view_type == 'family':
        # Get first family group the user belongs to
        family = request.user.families.first()
        if family:
            users_in_family = family.members.all()
            income_data = Income.objects.filter(user__in=users_in_family).aggregate(Sum('amount'))
            expense_data = Expense.objects.filter(user__in=users_in_family).aggregate(Sum('amount'))
        else:
            income_data = Income.objects.filter(user=request.user).aggregate(Sum('amount'))
            expense_data = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))
            messages.info(request, "You are not in a Family Group. Showing personal data.")
    else:
        income_data = Income.objects.filter(user=request.user).aggregate(Sum('amount'))
        expense_data = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))

    total_income = income_data['amount__sum'] or Decimal('0.00')
    total_expense = expense_data['amount__sum'] or Decimal('0.00')
    balance = total_income - total_expense
    
    check_expense_limit(request.user, request)

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "view_type": view_type,
    }

    return render(request, "dashboard.html", context)"""

dash_replacement = """@login_required
def dashboard(request):
    view_type = request.GET.get('view', 'personal')
    
    if view_type == 'family':
        family = request.user.families.first()
        if family:
            users_in_family = family.members.all()
            income_data = Income.objects.filter(user__in=users_in_family).aggregate(Sum('amount'))
            expense_data = Expense.objects.filter(user__in=users_in_family).aggregate(Sum('amount'))
            saving_data = Saving.objects.filter(user__in=users_in_family).aggregate(Sum('amount'))
        else:
            income_data = Income.objects.filter(user=request.user).aggregate(Sum('amount'))
            expense_data = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))
            saving_data = Saving.objects.filter(user=request.user).aggregate(Sum('amount'))
            messages.info(request, "You are not in a Family Group. Showing personal data.")
    else:
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

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_saving": total_saving,
        "balance": balance,
        "view_type": view_type,
        "recent_transactions": all_recent,
    }

    return render(request, "dashboard.html", context)"""

content = content.replace(dash_target, dash_replacement)

# 3. Scan Receipt
scan_target = """                amount = float(data.get("amount", 0))
                cat_name = data.get("category", "Other").strip().title()
                desc = data.get("description", "Receipt Scan")"""

scan_replacement = """                amount_str = str(data.get("amount", "0")).replace(',', '')
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0
                    
                cat_name = data.get("category", "Other").strip().title()
                desc = data.get("description", "Receipt Scan")"""

content = content.replace(scan_target, scan_replacement)

# 4. Export CSV
export_target = """@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Amount'])

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    for e in expenses:
        writer.writerow([e.date, e.category.name, e.description, e.amount])

    return response"""

export_replacement = """@login_required
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

    return response"""

content = content.replace(export_target, export_replacement)

# 5. Adding Saving CRUD Views
saving_crud = """

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
"""

content += saving_crud

with open("tracker/views.py", "w", encoding="utf-8") as f:
    f.write(content)
