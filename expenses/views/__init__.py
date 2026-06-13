from .auth_views import register, login
from .category_views import category_list, category_detail
from .expense_views import (
    expense_list,
    expense_detail,
    expense_summary,
    monthly_summary,
)

__all__ = [
    "register",
    "login",
    "category_list",
    "category_detail",
    "expense_list",
    "expense_detail",
    "expense_summary",
    "monthly_summary",
]
