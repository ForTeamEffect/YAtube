# deals/tests/tests_form.py
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment
from http import HTTPStatus

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            description='Тестовое описание')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': 'Тестовый текст',
            'image': uploaded,
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif',
                group=PostFormsTests.group
            ).exists()
        )
        post = Post.objects.first()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostFormsTests.group)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, f'/profile/{self.user.username}/')

    def test_post_edit(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        group2 = Group.objects.create(
            title='test_group2',
            description='Тестовое описание')
        form_data = {
            'author': self.user,
            'text': 'Текст из формы',
            'group': group2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.pk]),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Текст из формы',
                group=group2
            ).exists()
        )
        post = Post.objects.get(id=post.id)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.pk)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, f'/posts/{post.pk}/')

    def test_unauth_user_cant_publish_post(self):
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        first_count_posts = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), first_count_posts)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_unauth_user_cant_edit_post(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        form_data = {
            'author': self.user,
            'text': 'Текст из формы',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=[post.pk]),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый пост',
            ).exists()
        )
        # self.assertEqual(post.text, form_data['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_unauth_user_cant_publish_comment(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        count_comments = len(
            Comment.objects.select_related('post').filter(post=post)
        )
        form_data = {
            'text': 'Тестовый комент'
        }

        self.guest_client.post(
            reverse('posts:post_detail', args=[post.pk]),
            data=form_data,
            follow=True
        )
        count_comments_after_post = len(
            Comment.objects.select_related('post').filter(post=post)
        )
        self.assertEqual(count_comments, count_comments_after_post)

    def test_auth_user_publish_comment(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        count_comments = len(
            Comment.objects.select_related('post').filter(post=post)
        )
        form_data = {
            'text': 'Тестовый комент'
        }

        self.authorized_client.post(
            reverse('posts:post_detail', args=[post.pk]),
            data=form_data,
            follow=True
        )
        count_comments_after_post = len(
            Comment.objects.select_related('post').filter(post=post)
        )
        self.assertEqual(count_comments + 1, count_comments_after_post)
