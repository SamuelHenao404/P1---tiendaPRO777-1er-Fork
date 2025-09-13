from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render

from .models import Category, Item


# Create your views here.
def index(request):
    items = Item.objects.filter(is_sold=False)[:8]
    for item in items:
        if item.is_on_sale:
            item.discount = item.discounted_price()
    return render(
        request,
        "items/index.html",
        {
            "items": items,
        },
    )


def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.is_on_sale:
        item.discount = item.discounted_price()
    return render(
        request,
        "items/detail.html",
        {
            "item": item,
        },
    )


def browse(request):
    query = request.GET.get("query", "")
    category_id = request.GET.get("category", 0)
    categories = Category.objects.all()
    items = Item.objects.filter(is_sold=False)

    if category_id:
        items = items.filter(category_id=category_id)

    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(
        request,
        "items/browse.html",
        {
            "items": items,
            "query": query,
            "categories": categories,
            "category_id": int(category_id),
        },
    )

def about(request):
    return render(request, "items/about.html")
