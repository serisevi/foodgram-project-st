import base64
import logging
from io import BytesIO
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import F
from django.http import FileResponse, HttpResponseRedirect
from django.views import View
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    FavoriteRecipes, Ingredient, Recipe, ShoppingCart
)
from users.models import Subscribers, User
from .filters import IngredientsFilter, RecipesFilter
from .paginations import Pagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    AddRecipeSerializer, FavoriteRecipesSerializer, GetRecipeSerializer,
    IngredientSerializer, ShoppingCartSerializer, SubscribeSerializer,
    SubscriptionsListSerializer
)


class ShortLinkRedirectView(View):
    """Представление для перенаправления коротких ссылок на рецепты."""
    
    def get(self, request, id):
        """Обработка GET-запроса для перенаправления на страницу рецепта."""
        recipe = get_object_or_404(Recipe, id=id)
        return HttpResponseRedirect(f'/recipes/{recipe.id}')


class AvatarView(APIView):
    """Представление для управления аватаром пользователя."""
    
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Обновление аватара пользователя."""
        if 'avatar' not in request.data:
            return Response(
                {'error': 'Аватар не был предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            image_data = request.data['avatar']
            if isinstance(image_data, str) and image_data.startswith('data:image'):
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
                
                request = self.request
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

    def delete(self, request):
        """Удаление аватара пользователя."""
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


class CustomUserViewSet(UserViewSet):
    """Представление для управления пользователями."""
    
    pagination_class = Pagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        """Определяет права доступа для разных действий."""
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        """Получает список подписок пользователя."""
        subscriptions = Subscribers.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsListSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path=r'(?P<id>\d+)/subscribe'
    )
    def subscribe(self, request, id):
        """Подписка/отписка от автора."""
        author = get_object_or_404(User, id=id)
        data = {
            'author': author.id,
            'user': request.user.id
        }
        
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            subscription, _ = Subscribers.objects.filter(
                author=author.id,
                user=request.user.id
            ).delete()
            if subscription:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': "Вы не подписаны на этого автора!"},
                status=status.HTTP_400_BAD_REQUEST
            )


class IngredientsViewSet(viewsets.ModelViewSet):
    """Представление для работы с ингредиентами."""
    
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
    http_method_names = ['get', ]


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для работы с рецептами."""
    
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = GetRecipeSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
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
        base_url = request.build_absolute_uri('/').rstrip('/')
        short_link = f"{base_url}/s/{recipe.id}"
        return Response({'short-link': short_link})

    @action(
    methods=['GET'],
    detail=False,
    permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок в формате TXT."""
        # Получаем данные из корзины
        shoppingcart = ShoppingCart.objects.filter(
            user=request.user
        ).values('recipe_id__ingredients__name').annotate(
            amount=F('recipe_id__recipeingredients__amount'),
            measure=F('recipe_id__ingredients__measurement_unit')
        ).order_by('recipe_id__ingredients__name')
        
        # Агрегируем ингредиенты
        ingredients = {}
        for ingredient in shoppingcart:
            name = ingredient['recipe_id__ingredients__name']
            amount = ingredient['amount']
            measure = ingredient['measure']
            if name not in ingredients:
                ingredients[name] = (amount, measure)
            else:
                ingredients[name] = (
                    ingredients[name][0] + amount,
                    measure
                )
        
        # Формируем текстовый файл
        content = "Foodgram - список покупок\n"
        content += f"Пользователь: {request.user.username}\n"
        content += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        if not ingredients:
            content += "Ваш список покупок пуст."
        else:
            content += "Ингредиенты:\n"
            for i, (ingredient, data) in enumerate(ingredients.items(), 1):
                amount, measure = data
                content += f"{i}. {ingredient} - {amount} {measure}\n"
        
        # Создаем и возвращаем текстовый файл
        text_buffer = BytesIO()
        text_buffer.write(content.encode('utf-8'))
        text_buffer.seek(0)
        
        return FileResponse(
            text_buffer,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path=r'(?P<id>\d+)/shopping_cart'
    )
    def shopping_cart(self, request, id):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=id)
        
        if request.method == 'POST':
            shoppingcart_status = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()
            
            if shoppingcart_status:
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        if request.method == 'DELETE':
            shoppingcart_status, _ = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            
            if shoppingcart_status:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response(
                {'errors': 'Рецепт не найден в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path=r'(?P<id>\d+)/favorite'
    )
    def favorite(self, request, id):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=id)
        
        if request.method == 'POST':
            favorite_status = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()
            
            if favorite_status:
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = FavoriteRecipesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        if request.method == 'DELETE':
            favorite_status, _ = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            
            if favorite_status:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response(
                {'errors': 'Рецепт не найден в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
