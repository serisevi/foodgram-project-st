from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.constants import DEFAULT_PAGES_LIMIT
from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart)
from users.models import Subscribers, User


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора рецепта."""
        user = self.context.get('request')
        return bool(user and user.user.is_authenticated
                    and Subscribers.objects.filter(
                        author=obj,
                        user=user.user).exists())


class HelperRecipeSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для корректного отображения рецептов
       в списке рецептов автора."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок для текущего
       пользователя."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar', read_only=True)

    class Meta:
        model = Subscribers
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора рецепта."""
        user = self.context.get('request').user
        return Subscribers.objects.filter(author=obj.author,
                                          user=user).exists()

    def get_recipes(self, obj):
        """Список рецептов автора."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', DEFAULT_PAGES_LIMIT)
        try:
            limit = int(limit)
        except ValueError:
            pass
        return HelperRecipeSerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True
        ).data

    def get_recipes_count(self, obj):
        """Кол-во рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    class Meta:
        model = Subscribers
        fields = '__all__'

    def validate(self, data):
        """Валидация на подписку."""
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if Subscribers.objects.filter(author=data['author'],
                                      user=data['user']).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        return data

    def to_representation(self, author):
        return SubscriptionsListSerializer(author, context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный cериалайзер для корректного отображения
       Ингредиентов - рецепта."""
    id = serializers.ReadOnlyField(
        source='ingredients.id')
    name = serializers.ReadOnlyField(
        source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Cериалайзер для метода GET модели рецептов."""
    author = UsersSerializer(read_only=True)
    ingredients = GetRecipeIngredientSerializer(many=True,
                                                source='recipeingredients',
                                                read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Являяется ли рецепт избранным для текущего пользователя."""
        user = self.context.get('request')
        return bool(user and user.user.is_authenticated
                    and FavoriteRecipes.objects.filter(
                        recipe=obj,
                        user=user.user).exists())

    def get_is_in_shopping_cart(self, obj):
        """Является ли рецепт в списке покупок для текущего пользователя."""
        user = self.context.get('request')
        return bool(user and user.user.is_authenticated
                    and ShoppingCart.objects.filter(
                        recipe=obj,
                        user=user.user).exists())


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный cериалайзер для корректного добавления
       Ингредиентов в рецепт при его создании."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Cериалайзер для метода Post, PATCH и DEL модели рецептов."""
    ingredients = AddRecipeIngredientSerializer(many=True, write_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def add_ingredients(self, ingredients, recipe):
        """Сохранение в БД ингридиентов рецепта."""
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount'])

    def validate(self, data):
        """Валидация при создании рецепта."""
        ingredients = data.get('ingredients')
        image = data.get('image')
        if not ingredients:
            raise serializers.ValidationError('Укажите необходимые'
                                              ' ингридиенты для рецепта!')
        ingredients_id_list = [id['id'] for id in ingredients]
        if len(ingredients_id_list) != len(set(ingredients_id_list)):
            raise serializers.ValidationError('Вы указали одинаковые '
                                              'ингридиенты при создании '
                                              'рецепта!')
        if not image:
            raise serializers.ValidationError('Вы не указали картинку '
                                              'рецепта!')
        return data

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        """Внесение изменений в рецепт."""
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        recipe = super().update(recipe, validated_data)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, recipe):
        """Корректировка отображения информации о созданном рецепте."""
        return GetRecipeSerializer(recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Списка покупок."""
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipesSerializer(ShoppingCartSerializer):
    """Сериализатор для модели Избранных рецептов."""

    class Meta:
        model = FavoriteRecipes
        fields = ('id', 'name', 'image', 'cooking_time')
