from allauth.account.forms import SignupForm
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.db import models
from django.db.models import Sum
from django.urls import reverse


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, )
    rating = models.IntegerField(default=0)


    def update_rating(self):
        rating_posts_author = Post.objects.filter(author_id=self.pk).aggregate(rating=Sum('rating'))['rating']
        rating_comments_author = Comment.objects.filter(user_id=self.user).aggregate(rating=Sum('rating'))['rating']
        rating_comments_posts = Comment.objects.filter(post__author__user=self.user).aggregate(rating=Sum('rating'))[
            'rating']
        self.rating = rating_posts_author * 3 + rating_comments_author + rating_comments_posts
        self.save()


class Category(models.Model):
    culture = 'Культура'
    cience = 'Наука'
    tech = 'Технология'
    politics = 'Политика'
    sport = 'Спорт'
    entertainment = 'Развлечения'
    economics = 'Экономика'
    education = 'Образование'

    CATEGORIES = [
        (culture, 'Культура'),
        (cience, 'Наука'),
        (tech, 'Технология'),
        (politics, 'Политика'),
        (sport, 'Спорт'),
        (entertainment, 'Развлечения'),
        (economics, 'Экономика'),
        (education, 'Образование')
    ]
    cat = models.CharField(max_length=25, choices=CATEGORIES, default=politics)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.cat.title()


class Post(models.Model):
    news = 'NEWS'
    articl = 'ARTICL'
    TYPE = [
        (news, 'Новость'),
        (articl, 'Статья'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=25, choices=TYPE, default=news)
    date_create = models.DateTimeField(auto_now_add=True)
    category_post = models.ManyToManyField('Category')
    heading = models.CharField(max_length=255)
    text = models.CharField(max_length=50000)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124]

    def __str__(self):
        return f'{self.heading.title()}: {self.text[:30]}'

    # def get_absolute_url(self):
    #     return reverse('news', #args=[str(self.id)]
    #                    )

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'news-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его



class Postcategory(models.Model):
    post_c = models.ForeignKey(Post, on_delete=models.CASCADE)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, )
    text_comment = models.CharField(max_length=500)
    date_create_comment = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user