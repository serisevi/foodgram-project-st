from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import TEXT_MAX_LENGTH
from users.models import User


class Ingredient(models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название',
        help_text='Укажите название'
    )
    measurement_unit = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Единицы измерения',
        help_text='Укажите единицы измерения'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return self.name


class Recipe(models.Model):
    """Модель для хранения рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Укажите автора'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиент',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Укажите изображение',
        upload_to='recipes_images'
    )
    name = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название',
        help_text='Укажите название'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления, от 1 мин'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Строковое представление модели."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи между рецептами и ингредиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт',
        help_text='Укажите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент',
        default=1
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Кол-во ингредиента',
        help_text='Укажите кол-во ингредиента, от 1 и более'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('recipe',)
        verbose_name = 'Ингредиенты рецептов'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredients'
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return (
            f'{self.recipe}: {self.ingredient} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class ShoppingCart(models.Model):
    """Модель для хранения списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='пользователь',
        help_text='Укажите пользователя'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('recipe',)
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return f"{self.recipe} - {self.user}"


class FavoriteRecipes(models.Model):
    """Модель для хранения избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='пользователь',
        help_text='Укажите пользователя'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('recipe',)
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return f"{self.recipe} - {self.user}"
