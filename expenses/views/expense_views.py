from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Expense
from ..serializers import ExpenseSerializer
from .. import currency, alerts


def _convert_safe(amount, from_currency):
    try:
        return currency.convert(amount, from_currency, currency.BASE_CURRENCY)
    except Exception:
        return amount


def _filter_expenses(request):
    expenses = Expense.objects.filter(owner=request.user)
    params = request.query_params

    start_date = params.get("start_date")
    end_date = params.get("end_date")
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    search = params.get("search")
    if search:
        expenses = expenses.filter(title__icontains=search)
    category = params.get("category")
    if category:
        expenses = expenses.filter(category_id=category)
    min_amount = params.get("min_amount")
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    max_amount = params.get("max_amount")
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)

    return expenses


def _month_total(category, year, month, exclude_id=None):
    qs = category.expenses.filter(date__year=year, date__month=month)
    if exclude_id is not None:
        qs = qs.exclude(pk=exclude_id)
    total = Decimal("0")
    for exp in qs:
        total += _convert_safe(exp.amount, exp.currency)
    return total


def _check_budget(expense):
    category = expense.category
    if category.monthly_limit is None:
        return

    year, month = expense.date.year, expense.date.month
    total_after = _month_total(category, year, month)
    this_amount = _convert_safe(expense.amount, expense.currency)
    total_before = total_after - this_amount

    limit = category.monthly_limit
    if total_before <= limit < total_after:
        period = expense.date.strftime("%B %Y")
        alerts.send_budget_alert(
            category_name=category.name,
            spent=f"{total_after:.2f}",
            limit=f"{limit:.2f}",
            currency=currency.BASE_CURRENCY,
            period=period,
        )


@api_view(["GET", "POST"])
def expense_list(request):
    if request.method == "GET":
        expenses = _filter_expenses(request)
        serializer = ExpenseSerializer(
            expenses, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = ExpenseSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    expense = serializer.save(owner=request.user)
    _check_budget(expense)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, owner=request.user)
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ExpenseSerializer(expense, context={"request": request})
        return Response(serializer.data)

    if request.method in ("PUT", "PATCH"):
        serializer = ExpenseSerializer(
            expense,
            data=request.data,
            partial=(request.method == "PATCH"),
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        _check_budget(expense)
        return Response(serializer.data)

    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def expense_summary(request):
    base = currency.BASE_CURRENCY
    expenses = Expense.objects.filter(owner=request.user).select_related("category")

    totals: dict[str, Decimal] = {}
    for exp in expenses:
        converted = _convert_safe(exp.amount, exp.currency)
        totals[exp.category.name] = (
            totals.get(exp.category.name, Decimal("0")) + converted
        )

    return Response(
        {
            "base_currency": base,
            "categories": [
                {"category": name, "total": f"{total:.2f}"}
                for name, total in sorted(totals.items())
            ],
        }
    )


@api_view(["GET"])
def monthly_summary(request):
    base = currency.BASE_CURRENCY
    expenses = Expense.objects.filter(owner=request.user)

    totals: dict[str, Decimal] = {}
    for exp in expenses:
        key = exp.date.strftime("%Y-%m")
        converted = _convert_safe(exp.amount, exp.currency)
        totals[key] = totals.get(key, Decimal("0")) + converted

    months = [
        {"month": month, "total": f"{total:.2f}"}
        for month, total in sorted(totals.items(), reverse=True)
    ]
    return Response({"base_currency": base, "months": months})
