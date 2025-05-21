import base64
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe, ShoppingCart
)
from users.models import Subscribers, User
from .filters import IngredientsFilter, RecipesFilter
from .paginations import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AddRecipeSerializer, AuthorWithRecipesSerializer,
    GetRecipeSerializer, IngredientSerializer
)


class ShortLinkRedirectView(View):
    """Представление для перенаправления коротких ссылок на рецепты."""

    def get(self, request, pk):
        """Обработка GET-запроса для перенаправления на страницу рецепта."""
        # Перенаправляем на страницу рецепта в UI
        return redirect(f'/recipes/{pk}/')


class CustomUserViewSet(UserViewSet):
    """Представление для управления пользователями."""

    pagination_class = Pagination

    def get_permissions(self):
        """Определяет права доступа для разных действий."""
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Управление аватаром пользователя."""
        if request.method == 'DELETE':
            user = request.user
            if not user.avatar:
                return Response(
                    {'error': 'У пользователя нет аватара'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.avatar.delete()
            user.avatar = None
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        if 'avatar' not in request.data:
            return Response(
                {'error': 'Аватар не был предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_data = request.data['avatar']
            if (isinstance(image_data, str)
                    and image_data.startswith('data:image')):
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'avatar.{ext}'
                )

                user = request.user
                if user.avatar:
                    user.avatar.delete()
                user.avatar = data
                user.save()

                avatar_url = request.build_absolute_uri(user.avatar.url)
                return Response(
                    {'avatar': avatar_url},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Неверный формат данных изображения'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при обработке изображения: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получает список подписок пользователя."""
        # Получаем авторов, на которых подписан текущий пользователь
        authors = User.objects.filter(authors__user=request.user).distinct()
        pages = self.paginate_queryset(authors)
        serializer = AuthorWithRecipesSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписка/отписка от автора."""
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = Subscribers.objects.get_or_create(
                author=author,
                user=request.user
            )

            if not created:
                return Response(
                    {'errors': f'Вы уже подписаны на {author.username}!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = AuthorWithRecipesSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Subscribers,
            author=author,
            user=request.user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от типа запроса."""
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return AddRecipeSerializer

    @action(
        methods=['GET'],
        detail=True,
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Генерирует короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, id=pk)
        short_link_path = reverse('short-link', kwargs={'pk': recipe.id})
        short_link = request.build_absolute_uri(short_link_path)
        return Response({'short-link': short_link})

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок в формате TXT."""
        # Получаем все рецепты из корзины пользователя
        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        recipes = [item.recipe for item in shopping_cart_items]

        # Формируем заголовок текстового файла
        content = "Foodgram - список покупок\n"
        content += f"Пользователь: {request.user.username}\n"
        content += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"

        if not recipes:
            content += "Ваш список покупок пуст."
            return FileResponse(
                content,
                as_attachment=True,
                filename='shopping_list.txt',
                content_type='text/plain; charset=utf-8'
            )

        # Добавляем информацию о рецептах и авторах
        content += "Рецепты в вашем списке:\n"
        for i, recipe in enumerate(recipes, 1):
            content += (f"{i}. {recipe.name} - "
                        f"автор: {recipe.author.username}\n")

        content += "\nИнгредиенты для приготовления:\n"

        # Получаем данные ингредиентов из корзины
        shoppingcart = ShoppingCart.objects.filter(
            user=request.user
        ).values('recipe__ingredients__name').annotate(
            amount=F('recipe__recipeingredients__amount'),
            measure=F('recipe__ingredients__measurement_unit')
        ).order_by('recipe__ingredients__name')

        # Агрегируем ингредиенты
        ingredients = {}
        for ingredient in shoppingcart:
            name = ingredient['recipe__ingredients__name']
            amount = ingredient['amount']
            measure = ingredient['measure']
            if name not in ingredients:
                ingredients[name] = (amount, measure)
            else:
                ingredients[name] = (
                    ingredients[name][0] + amount,
                    measure
                )

        # Добавляем ингредиенты в файл
        for i, (ingredient, data) in enumerate(ingredients.items(), 1):
            amount, measure = data
            content += f"{i}. {ingredient} - {amount} {measure}\n"

        return FileResponse(
            content,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            shoppingcart_status = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()

            if shoppingcart_status:
                return Response(
                    {'errors': f'Рецепт "{recipe.name}" уже есть в списке!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = GetRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shoppingcart = get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=recipe
            )
            shoppingcart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            favorite_status = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()

            if favorite_status:
                return Response(
                    {'errors': f'Рецепт "{recipe.name}" уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            FavoriteRecipes.objects.create(user=request.user, recipe=recipe)
            serializer = GetRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = get_object_or_404(
                FavoriteRecipes,
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
