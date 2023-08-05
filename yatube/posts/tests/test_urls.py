from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Group, Post
from django.core.cache import cache

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            # slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user_who_not_create = \
            User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_who_not_create = Client()
        # Авторизуем пользователя
        self.authorized_who_not_create.force_login(self.user_who_not_create)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_is_available(self):
        urls_codes = {
            f'/posts/{self.post.pk}/edit/':
                f'/auth/login/?next=/posts/{self.post.pk}/edit/',
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/profile/{self.user_who_not_create.username}/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            '/': HTTPStatus.OK,
            '/create/': '/auth/login/?next=/create/',

        }
        for address, st_code_or_redirect_url in urls_codes.items():

            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if st_code_or_redirect_url != HTTPStatus.OK:
                    self.assertRedirects(response, st_code_or_redirect_url)
                else:
                    self.assertEqual(
                        response.status_code, st_code_or_redirect_url)
