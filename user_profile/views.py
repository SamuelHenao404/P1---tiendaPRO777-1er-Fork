from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from items.models import PurchaseReceipt


@login_required(login_url="login")
def user_profile(request):
    return render(request, "user_profile/profile.html")


@login_required(login_url="login")
def purchase_history(request):
    receipts = list(PurchaseReceipt.objects.filter(buyer=request.user))
    return render(
        request,
        "user_profile/purchase_history.html",
        {
            "receipts": receipts,
        },
    )
