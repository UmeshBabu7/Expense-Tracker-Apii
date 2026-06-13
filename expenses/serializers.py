from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Expense


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "monthly_limit"]

    def validate_name(self, value):
        owner = self.context["request"].user
        qs = Category.objects.filter(owner=owner, name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You already have a category with this name."
            )
        return value


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
