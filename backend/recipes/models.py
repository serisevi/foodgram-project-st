from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram.constants import TEXT_MAX_LENGTH
from users.models import User


class Ingredient(models.Model):
    """Модель для хранения ингредиентов."""
    
    name = models.CharField(
        unique=True,
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название ингредиента',
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Единицы измерения',
        help_text='Укажите единицы измерения'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('id', 'name')
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
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиент рецепта',
    )
    is_favorited = models.BooleanField(
        default=True,
        verbose_name='Находится в избранном',
        help_text='Отметьте рецепт в избранное'
    )
    is_in_shopping_cart = models.BooleanField(
        default=True,
        verbose_name='Находится в корзине',
        help_text='Отложите рецепт в корзину'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        help_text='Укажите изображение рецепта',
        upload_to='recipes_images'
    )
    name = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Укажите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления'),
            MaxValueValidator(32000, 'Максимальное время приготовления'),
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
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент рецепта',
        help_text='Укажите ингредиент рецепта'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное кол-во ингредиента'),
            MaxValueValidator(32000, 'Максимальное кол-во ингредиента'),
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
                fields=['recipe', 'ingredients'],
                name='unique_recipe_ingredients'
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return (
            f'{self.recipe}: {self.ingredients} - {self.amount} '
            f'{self.ingredients.measurement_unit}'
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
