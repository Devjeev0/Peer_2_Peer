from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from loans.models import *
from .forms import CustomUserCreationForm

def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log in the user after signup
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def custom_logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Fetch loans where the user is the investor (via Funded_loans)
    # We want the Loan objects, so we can query Funded_loans and get the related loans
    funded_loans_records = Funded_loans.objects.filter(user_id=request.user)
    investments = [record.loan for record in funded_loans_records]
    
    # Fetch loans where the user is the borrower (now 'user' field)
    loans = Loan.objects.filter(user=request.user)
    
    try:
        balance = MyBalance.objects.get(user_id=request.user)
    except MyBalance.DoesNotExist:
        balance = None

    return render(request, 'dashboard.html', {
        'investments': investments,
        'loans': loans,
        'balance': balance
    })


# @login_required
# def investor_dashboard(request):
#     investments = Loan.objects.filter(investor=request.user)
#     return render(request, 'investor_dashboard.html', {'investments': investments})

# @login_required
# def borrower_dashboard(request):
#     loans = Loan.objects.filter(borrower=request.user)
#     return render(request, 'borrower_dashboard.html', {'loans': loans})
