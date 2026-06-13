from django.contrib import admin
from ..models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "currency", "category", "date", "owner")
    list_filter = ("owner", "currency", "category", "date")
    search_fields = ("title", "notes")
    date_hierarchy = "date"
