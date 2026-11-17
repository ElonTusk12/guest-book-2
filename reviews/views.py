from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ReviewForm
from .models import Review


@require_GET
def index(request):
    return redirect("reviews:review_list")


@require_http_methods(["GET", "POST"])
def review_list(request):
    status = 200
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reviews:review_list")
        status = 400
    else:
        form = ReviewForm()

    reviews = Review.objects.all()
    return render(
        request,
        "reviews/review_list.html",
        {"reviews": reviews, "form": form},
        status=status,
    )
