from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from peer2peer_project.models import Loan, Payment, MyBalance, Deposit, Funded_loans
from .forms import LoanRequestForm
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal

# loans/utils.py
def calculate_simple_interest(principal, annual_rate_percent, years):
    return (principal * years * annual_rate_percent) / 100

def calculate_compound_interest(principal, annual_rate_percent, years, compounds_per_year=1):
    # Compound interest formula: A = P * (1 + r/n)^(n*t) - P
    r = annual_rate_percent / 100
    amount = principal * (1 + r/compounds_per_year) ** (compounds_per_year * years)
    return amount - principal

def schedule_payments(loan):
    # Determine total months based on loan type
    if loan.loan_type == 'Custom' and loan.custom_days:
        # For custom days, we might treat it as a single payment or approximate months
        # For simplicity, let's treat it as 1 month equivalent for now or just use duration_months if set
        total_months = 1 
    else:
        total_months = loan.duration_months if loan.duration_months else 1

    principal = loan.amount
    # rate = float(loan.interest_rate) # rate might be None or Decimal
    rate = float(loan.interest_rate) if loan.interest_rate else 0.0
    
    # Calculate total amount (simple interest for illustration)
    # Adjust interest calculation based on time
    total_interest = (principal * total_months * Decimal(rate)) / (100*12)
    total_payment = principal + total_interest
    monthly_payment = total_payment / total_months

    start_date = date.today()
    for m in range(1, total_months+1):
        due = start_date + timedelta(days=30*m)  # roughly monthly
        # Payment model now uses user_id, which is the borrower
        Payment.objects.create(loan=loan, user_id=loan.user, due_date=due, amount=monthly_payment)

@login_required
def request_loan(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.status = 'requested'
            loan.save()
            return redirect('dashboard')
    else:
        form = LoanRequestForm()
    return render(request, 'loans/request_loan.html', {'form': form})

@login_required
def fund_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id, status='requested')
    
    if loan.user == request.user:
        messages.error(request, "You cannot fund your own loan.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        investor_balance, created = MyBalance.objects.get_or_create(user_id=request.user)
        
        if investor_balance.balance < loan.amount:
            messages.error(request, "Insufficient funds to fund this loan.")
            return render(request, 'loans/fund_loan.html', {'loan': loan})

        # Deduct from investor
        investor_balance.balance -= loan.amount
        investor_balance.save()
        
        # Add to borrower
        borrower_balance, created = MyBalance.objects.get_or_create(user_id=loan.user)
        borrower_balance.balance += loan.amount
        borrower_balance.save()
        
        # Update loan
        rate = request.POST.get('interest_rate')
        loan.interest_rate = rate
        # loan.investor = request.user  <-- Removed
        loan.status = 'funded'
        loan.save()
        
        # Create Funded_loans record
        Funded_loans.objects.create(
            loan=loan,
            user_id=request.user, # Investor
            amount=loan.amount
        )
        
        # Schedule payments
        schedule_payments(loan)
        
        return redirect('dashboard')
        
    return render(request, 'loans/fund_loan.html', {'loan': loan})

@login_required
def list_requested_loans(request):
    loans = Loan.objects.filter(status='requested')
    return render(request, 'loans/list_requested_loans.html', {'loans': loans})

@login_required
def make_payment(request, loan_id):
    loan = Loan.objects.get(id=loan_id, user=request.user)
    payments = Payment.objects.filter(loan=loan, paid=False).order_by('due_date')
    
    if not payments.exists():
         messages.info(request, "No pending payments for this loan.")
         return redirect('dashboard')
    
    next_payment = payments.first()
    
    if request.method == 'POST':
        borrower_balance, created = MyBalance.objects.get_or_create(user_id=request.user)
        
        if borrower_balance.balance < next_payment.amount:
            messages.error(request, "Insufficient funds to make this payment.")
            return render(request, 'loans/make_payments.html', {'loan': loan, 'payment': next_payment})

        # Deduct from borrower
        borrower_balance.balance -= next_payment.amount
        borrower_balance.save()
        
        # Check if this was the last payment
        if payments.count() == 1:
            loan.status = 'repaid'
            loan.save()
            
        # Add to investor
        # We need to find the investor from Funded_loans
        funded_loan_record = Funded_loans.objects.filter(loan=loan).first()
        if funded_loan_record:
            investor_user = funded_loan_record.user_id
            investor_balance, created = MyBalance.objects.get_or_create(user_id=investor_user)
            investor_balance.balance += next_payment.amount
            investor_balance.save()
            
        next_payment.paid = True
        next_payment.paid_at = timezone.now()
        next_payment.save()
        
        messages.success(request, "Payment successful!")
        return redirect('dashboard')
    
    return render(request, 'loans/make_payments.html', {'loan': loan, 'payment': next_payment})

@login_required
def my_balance(request):
    balance, created = MyBalance.objects.get_or_create(user_id=request.user)
    return render(request, 'loans/my_balance.html', {'balance': balance})

@login_required
def deposit(request):
    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        Deposit.objects.create(user_id=request.user, amount=amount)
        balance, created = MyBalance.objects.get_or_create(user_id=request.user)
        balance.balance += amount
        balance.save()
        return redirect('my_balance')
    return render(request, 'loans/deposit.html')

@login_required
def transaction_history(request):
    # Get deposits
    deposits = Deposit.objects.filter(user_id=request.user)
    
    # Get funded loans (investor side - money out)
    # Funded_loans where user_id is the current user (investor)
    funded_loans = Funded_loans.objects.filter(user_id=request.user)
    
    try:
        balance = MyBalance.objects.get(user_id=request.user)
        current_balance = balance.balance
    except MyBalance.DoesNotExist:
        current_balance = 0

    # Get received loans (borrower side - money in)
    # Loans where the current user is the borrower (loan.user)
    # We query Funded_loans to see which of my loans have been funded
    received_loans = Funded_loans.objects.filter(loan__user=request.user)
    
    # Get payments made by user (as borrower - money out)
    payments_made = Payment.objects.filter(loan__user=request.user, paid=True)
    
    # Get payments received by user (as investor - money in)
    # Payments for loans that I have funded
    # 1. Get loans I funded
    my_funded_loans_ids = Funded_loans.objects.filter(user_id=request.user).values_list('loan_id', flat=True)
    # 2. Get payments for those loans
    payments_received = Payment.objects.filter(loan__id__in=my_funded_loans_ids, paid=True)
    
    # Create unified transaction list
    transactions = []
    
    for deposit in deposits:
        transactions.append({
            'type': 'deposit',
            'amount': deposit.amount,
            'date': deposit.created_at,
            'description': 'Deposit to wallet',
            'balance': current_balance # Note: This is current balance, not historical
        })
    
    for funded in funded_loans:
        transactions.append({
            'type': 'funded_loan',
            'amount': funded.amount,
            'date': funded.created_at,
            'description': f'Funded Loan to - {funded.loan.user.username}',
            'balance': current_balance
        })
        
    for received in received_loans:
        transactions.append({
            'type': 'loan_received',
            'amount': received.amount,
            'date': received.created_at,
            'description': f'Received Loan #{received.loan.id}',
            'balance': current_balance  
        })
    
    for payment in payments_made:
        transactions.append({
            'type': 'payment_out',
            'amount': payment.amount,
            'date': payment.paid_at,
            'description': f'Payment for Loan #{payment.loan.id}',
            'balance': current_balance
        })
    
    for payment in payments_received:
        transactions.append({
            'type': 'payment_in',
            'amount': payment.amount,
            'date': payment.paid_at,
            'description': f'Payment received from Loan - {payment.loan.user.username}',
            'balance': current_balance
        })  
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return render(request, 'loans/transaction_history.html', {'transactions': transactions})