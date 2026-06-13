from django.urls import path

from . import views

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("categories/", views.category_list, name="category-list"),
    path("categories/<int:pk>/", views.category_detail, name="category-detail"),
    path("expenses/", views.expense_list, name="expense-list"),
    path("expenses/summary/", views.expense_summary, name="expense-summary"),
    path(
        "expenses/monthly-summary/",
        views.monthly_summary,
        name="expense-monthly-summary",
    ),
    path("expenses/<int:pk>/", views.expense_detail, name="expense-detail"),
]
