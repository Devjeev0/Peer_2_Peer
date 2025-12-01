from django.urls import path
from . import views

urlpatterns = [
    path('request_loan/', views.request_loan, name='request_loan'),
    path('fund_loan/<int:loan_id>/', views.fund_loan, name='fund_loan'),
    path('loans/', views.list_requested_loans, name='list_requested_loans'),
    path('make_payments/<int:loan_id>/', views.make_payment, name='make_payments'),
    path('my_balance/', views.my_balance, name='my_balance'),
    path('deposit/', views.deposit, name='deposit'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),
]