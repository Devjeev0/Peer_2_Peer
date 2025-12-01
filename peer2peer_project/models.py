# loans/models.py
from django.conf import settings
from django.db import models


class Loan(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('funded', 'Funded'),
        ('repaid', 'Repaid'),
        ('rejected', 'Rejected')
    ]
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    ANNUAL = 'Annual'
    CUSTOM = 'Custom'

    BORROW_CHOICE = [
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (ANNUAL, 'Annual'),
        (CUSTOM, 'Custom')
    ]

    PURPOSE_CHOICES = [
        ('Business', 'Business'),
        ('Education', 'Education'),
        ('Personal', 'Personal'),
        ('Medical', 'Medical'),
        ('Home Improvement', 'Home Improvement'),
        ('Debt Consolidation', 'Debt Consolidation'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans_taken')
    # investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='loans_given')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_months = models.IntegerField(null=True, blank=True)
    custom_days = models.IntegerField(null=True, blank=True, help_text="Enter number of days for Custom loan type")
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='Personal')
    loan_type = models.CharField(max_length=10, choices=BORROW_CHOICE, default='Weekly')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan {self.id} - {self.user.username} - {self.amount}"


class Funded_loans(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Funded {self.amount} for Loan {self.loan.id} by {self.user_id.username}"


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Loan {self.loan.id} - Due {self.due_date}"


class MyBalance(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Balance for {self.user_id.username} - {self.balance}"


class Deposit(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Deposit for {self.user_id.username} - {self.amount}"

