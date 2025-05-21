from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportActionModelAdmin

from users.models import Subscribers, User
from .models import (Ingredient, Recipe, RecipeIngredient,
                     FavoriteRecipes, ShoppingCart)


# Настройка заголовков админ-сайта
admin.site.site_header = "Foodgram - Администрирование"
admin.site.site_title = "Foodgram"
admin.site.index_title = "Управление сайтом"


class SubscribersInline(admin.TabularInline):
    """Инлайн для подписчиков пользователя."""

    model = Subscribers
    min_num = 1
    extra = 0


class BaseHasRelationFilter(admin.SimpleListFilter):
    """Базовый класс для фильтров по наличию связей."""

    LOOKUP_CHOICES = (('1', 'Есть'), ('0', 'Нет'),)
    # Должен быть определен в дочерних классах
    relation_field = None

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(**{
                f'{self.relation_field}__isnull': False
            }).distinct()
        if self.value() == '0':
            return queryset.filter(**{
                f'{self.relation_field}__isnull': True
            })


class HasRecipesFilter(BaseHasRelationFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    relation_field = 'recipes'


class HasSubscriptionsFilter(BaseHasRelationFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    relation_field = 'subscribers'


class HasFollowersFilter(BaseHasRelationFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'
    relation_field = 'authors'


class HasRecipesIngredientFilter(BaseHasRelationFilter):
    title = 'Есть в рецептах'
    parameter_name = 'has_recipes'
    relation_field = 'recipes'


class UserAdmin(BaseUserAdmin):
    """Админ-модель для управления пользователями."""

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()

    @admin.display(description='Подписчиков')
    def followers_count(self, obj):
        """Возвращает количество подписчиков пользователя."""
        return obj.authors.count()

    @admin.display(description='Подписок')
    def subscriptions_count(self, obj):
        """Возвращает количество подписок пользователя."""
        return obj.subscribers.count()

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        """Отображает аватар пользователя."""
        if obj.avatar:
            return (
                '<img src="{}" width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover;" />'.format(
                    obj.avatar.url
                )
            )
        return (
            '<div style="width: 50px; height: 50px; background-color: #ccc; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; color: #fff; font-weight: bold;">'
            '{}</div>'.format(
                obj.username[0].upper()
            )
        )

    list_display = (
        'id',
        'avatar_preview',
        'username',
        'first_name',
        'last_name',
        'email',
        'recipes_count',
        'subscriptions_count',
        'followers_count',
    )
    list_filter = (
        'is_staff',
        HasRecipesFilter,
        HasSubscriptionsFilter,
        HasFollowersFilter,
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('avatar_preview',)

    fieldsets = (
        ('Личная информация', {
            'fields': (
                'username', 'first_name', 'last_name', 'email',
                'avatar', 'avatar_preview'
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )


class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    """Админ-модель для управления ингредиентами."""

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Возвращает количество рецептов с этим ингредиентом."""
        return obj.recipes.count()

    list_display = (
        'id',
        'name',
        'measurement_unit',
        'recipes_count',
    )
    list_filter = ('measurement_unit', HasRecipesIngredientFilter)
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов рецепта."""

    model = RecipeIngredient
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    """Админ-модель для управления рецептами."""

    @mark_safe
    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Получает список ингредиентов рецепта."""
        ingredients = obj.recipeingredients.all()
        return '<br>'.join(
            [
                f'{ingredient.ingredient.name} - {ingredient.amount} '
                f'{ingredient.ingredient.measurement_unit}'
                for ingredient in ingredients
            ]
        )

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        """Отображает кол-во пользователей, добавивших рецепт в избранное."""
        return obj.favoriterecipes.count()

    @mark_safe
    @admin.display(description='Изображение')
    def image_preview(self, obj):
        """Отображает изображение рецепта."""
        if obj.image:
            return (
                '<img src="{}" width="100" height="75" '
                'style="object-fit: cover; border-radius: 5px;" />'.format(
                    obj.image.url
                )
            )
        return (
            '<div style="width: 100px; height: 75px; '
            'background-color: #f0f0f0; display: flex; '
            'align-items: center; justify-content: center; '
            'border-radius: 5px;">Нет фото</div>'
        )

    @mark_safe
    @admin.display(description='Автор')
    def author_with_avatar(self, obj):
        """Отображает автора с аватаром."""
        if hasattr(obj.author, 'avatar') and obj.author.avatar:
            return (
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" width="30" height="30" '
                'style="border-radius: 50%; margin-right: 8px; '
                'object-fit: cover;" />{}</div>'.format(
                    obj.author.avatar.url, obj.author.username
                )
            )
        return (
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 30px; height: 30px; '
            'background-color: #ccc; border-radius: 50%; '
            'display: flex; align-items: center; '
            'justify-content: center; margin-right: 8px; '
            'color: #fff; font-weight: bold;">{}</div>{}</div>'.format(
                obj.author.username[0].upper(), obj.author.username
            )
        )

    inlines = (RecipeIngredientInline,)
    list_display = (
        'image_preview',
        'id',
        'name',
        'author_with_avatar',
        'cooking_time',
        'get_ingredients',
        'favorite_count',
    )
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'cooking_time')
    readonly_fields = ('image_preview',)
    empty_value_display = 'Не задано'

    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'name', 'image', 'image_preview')
        }),
        ('Описание рецепта', {
            'fields': ('text', 'cooking_time')
        }),
    )

    list_per_page = 10
    save_on_top = True


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-модель для управления ингредиентами в рецептах."""

    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe__name', 'ingredient__name')


class FavoriteRecipesAdmin(admin.ModelAdmin):
    """Админ-модель для управления избранными рецептами."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-модель для управления списком покупок."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')


class SubscribersAdmin(admin.ModelAdmin):
    """Админ-модель для управления подписками."""

    list_display = (
        'id',
        'author',
        'user',
    )
    search_fields = ('id', 'author__username', 'user__username')
    ordering = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscribers, SubscribersAdmin)
