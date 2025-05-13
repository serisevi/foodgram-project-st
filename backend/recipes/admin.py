from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin

from users.models import Subscribers, User
from .models import Ingredient, Recipe, RecipeIngredient


# Настройка заголовков админ-сайта
admin.site.site_header = "Foodgram - Администрирование"
admin.site.site_title = "Foodgram"
admin.site.index_title = "Управление сайтом"


class SubscribersInline(admin.TabularInline):
    """Инлайн для подписчиков пользователя."""
    
    model = Subscribers
    min_num = 1
    extra = 0


class UserAdmin(UserAdmin):
    """Админ-модель для управления пользователями."""

    @admin.display(description='Подписчики')
    def get_subscribers(self, obj):
        """Получает список подписчиков пользователя."""
        subscribers = Subscribers.objects.filter(author_id=obj.id)
        return [i.user for i in subscribers]
    
    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        """Отображает аватар пользователя."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background-color: #ccc; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; color: #fff; font-weight: bold;">{}</div>',
            obj.username[0].upper()
        )

    list_display = (
        'avatar_preview',
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'get_subscribers',
    )
    list_filter = ('is_staff',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('avatar_preview',)
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'avatar', 'avatar_preview')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )


class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    """Админ-модель для управления ингредиентами."""
    
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов рецепта."""
    
    model = RecipeIngredient
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    """Админ-модель для управления рецептами."""

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Получает список ингредиентов рецепта."""
        ingredients = obj.recipeingredients.all()
        return (
            ', '.join(
                [
                    f'{ingredient.ingredients} - {ingredient.amount} '
                    f'{ingredient.ingredients.measurement_unit}'
                    for ingredient in ingredients
                ]
            )
        )
    
    @admin.display(description='Изображение')
    def image_preview(self, obj):
        """Отображает изображение рецепта."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return format_html(
            '<div style="width: 100px; height: 75px; background-color: #f0f0f0; '
            'display: flex; align-items: center; justify-content: center; '
            'border-radius: 5px;">Нет фото</div>'
        )
    
    @admin.display(description='Автор')
    def author_with_avatar(self, obj):
        """Отображает автора с аватаром."""
        if hasattr(obj.author, 'avatar') and obj.author.avatar:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" width="30" height="30" '
                'style="border-radius: 50%; margin-right: 8px; object-fit: cover;" />'
                '{}</div>',
                obj.author.avatar.url, obj.author.username
            )
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 30px; height: 30px; background-color: #ccc; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; margin-right: 8px; color: #fff; '
            'font-weight: bold;">{}</div>{}</div>',
            obj.author.username[0].upper(), obj.author.username
        )

    inlines = (RecipeIngredientInline,)
    list_display = (
        'image_preview',
        'id',
        'name',
        'author_with_avatar',
        'cooking_time',
        'get_ingredients',
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
        ('Статус', {
            'fields': ('is_favorited', 'is_in_shopping_cart')
        }),
    )
    
    list_per_page = 10
    save_on_top = True


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
