from django.contrib import admin

from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "monthly_limit")
    list_filter = ("owner",)
    search_fields = ("name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "currency", "category", "date", "owner")
    list_filter = ("owner", "currency", "category", "date")
    search_fields = ("title", "notes")
    date_hierarchy = "date"
