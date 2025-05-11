from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportActionModelAdmin

from users.models import Subscribers, User
from .models import Ingredient, Recipe, RecipeIngredient


class SubscribersInline(admin.TabularInline):
    model = Subscribers
    min_num = 1


class UserAdmin(UserAdmin):

    @admin.display(description='Подписчики')
    def get_subscribers(self, obj):
        subscribers = Subscribers.objects.filter(author_id=obj.id)
        return [i.user for i in subscribers]

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'get_subscribers',
    )
    list_filter = ('username',)
    search_fields = ('username',)
    ordering = ('username',)


class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        ingredients = obj.recipeingredients.all()
        return (
            ', '.join(
                [f'{ingredient.ingredients} - {ingredient.amount} '
                 f'{ingredient.ingredients.measurement_unit}'
                 for ingredient in ingredients])
        )

    inlines = (RecipeIngredientInline,)
    list_display = (
        'id',
        'name',
        'author',
        'get_ingredients',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'Не задано'


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
