from django.contrib import admin
from ..models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "monthly_limit")
    list_filter = ("owner",)
    search_fields = ("name",)
