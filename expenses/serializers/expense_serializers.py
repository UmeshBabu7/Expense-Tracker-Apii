from rest_framework import serializers
from ..models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "currency",
            "category",
            "category_name",
            "date",
            "notes",
        ]

    def validate_currency(self, value):
        return value.upper()

    def validate_category(self, value):
        owner = self.context["request"].user
        if value.owner_id != owner.id:
            raise serializers.ValidationError("Category not found.")
        return value
