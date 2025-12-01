# loans/forms.py
from django.forms import ModelForm
from peer2peer_project.models import Loan

class LoanRequestForm(ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'duration_months', 'purpose', 'loan_type', 'custom_days', 'interest_rate']
