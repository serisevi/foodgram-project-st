from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientsFilter(SearchFilter):
    """Кастомная настройка фильтра для Ингридиентов."""
    search_param = 'name'


class RecipesFilter(rest_framework.FilterSet):
    """Кастомная настройка фильтра для Рецептов."""
    author = rest_framework.CharFilter(field_name='author')
    is_favorited = rest_framework.NumberFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует избранные рецепты пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты в списке рецептов пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')
