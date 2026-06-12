from django.db.models import Sum
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer, RegisterSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"id": user.id, "username": user.username, "token": token.key},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = User.objects.filter(username=username).first()
    if user is None or not user.check_password(password):
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["GET", "POST"])
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.filter(owner=request.user)
        serializer = CategorySerializer(
            categories, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = CategorySerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk, owner=request.user)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CategorySerializer(category, context={"request": request})
        return Response(serializer.data)

    if request.method in ("PUT", "PATCH"):
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=(request.method == "PATCH"),
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def expense_list(request):
    if request.method == "GET":
        expenses = Expense.objects.filter(owner=request.user)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)

        serializer = ExpenseSerializer(
            expenses, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = ExpenseSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
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
        serializer.save()
        return Response(serializer.data)

    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def expense_summary(request):
    summary = (
        Expense.objects.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("category__name")
    )
    return Response(list(summary))
