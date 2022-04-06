from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Наименование',
                            max_length=20, unique=True)
    color = models.CharField(verbose_name='Цвет в HEX',
                             max_length=7, unique=True, null=True)
    slug = models.SlugField(verbose_name='Слаг',
                            max_length=100, unique=True, null=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=100)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=30)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название рецепта', max_length=100)
    text = models.TextField(
        verbose_name='Описание рецепта', help_text='Введите описание рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientForRecipe',)
    tags = models.ManyToManyField(Tag, verbose_name='Тэг', related_name='tags')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator
                    (1, 'Время приготовления не может быть меньше минуты.')])
    image = models.ImageField(verbose_name='Картинка')
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, verbose_name='Автор')
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientForRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredients_amount')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='ingredients_amount')
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator
                    (1, 'Количество не может быть меньше 1.')])

    class Meta:
        unique_together = ('ingredient', 'recipe')
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='favourites')

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='favourites',
                               null=True, blank=True)

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное.'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='purchases')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='purchases')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
