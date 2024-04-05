from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from .exceptions import InsufficientFundsError,TryingToWithdrawSavingsTooSoon
import datetime

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saving_activated = models.BooleanField(default=False)
    saving_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saving_activated_date = models.DateField(null=True, blank=True)
    saving_activated_first_time = models.BooleanField(default=True)

    def transfer_funds(self, to_wallet, amount):
        with transaction.atomic():

            if self.saving_activated:
                total_amount = amount+1
                self.saving_amount+=1
            else:
                total_amount = amount

            if self.balance < total_amount:
                raise InsufficientFundsError()


            self.balance -= total_amount
            to_wallet.balance += amount
            self.save()
            to_wallet.save()

    
    def activate_saving(self):
        if self.saving_activated_first_time:
            self.saving_activated_date = datetime.date.today()
            self.saving_activated_first_time=False
        self.saving_activated = True
        self.save()


    def deactivate_saving(self):
        self.saving_activated = False
        self.save()


    def withdraw_savings(self):
        with transaction.atomic():
            if (datetime.date.today()-self.saving_activated_date).days>=365:
                if self.saving_amount<1:
                    raise InsufficientFundsError()
                else:
                    self.balance += self.saving_amount
                    self.saving_amount = 0
                    self.save()
            else:
                raise TryingToWithdrawSavingsTooSoon()


    def __str__(self):
        return f"{self.user.username}'s Wallet"



