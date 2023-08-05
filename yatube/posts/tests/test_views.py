import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django.urls import reverse
from posts.models import Group, Post, Comment, Follow
from django import forms
# from django.views.decorators import cache
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
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
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_reversed_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_reversed_names = {
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.pk}'}): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.pk}'}): 'posts/post_detail.html',
            reverse('posts:profile', kwargs={
                'username': f'{self.user}'}): 'posts/profile.html',
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_reversed_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_slug(self):
        obj_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                    )).context['page_obj'][0]
        self.assertEqual(self.group.slug, obj_group.group.slug)

    def test_author_post_profile(self):
        obj_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user}'}
                    )).context['page_obj'][0]
        self.assertEqual(self.user, obj_profile.author)

    def test_pk_post_detail(self):
        obg_post_detail = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.pk}'})).context['page_obj']
        self.assertEqual(self.post.pk, obg_post_detail.pk)

    def test_context(self):
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
        # Отправляем POST-запрос
        self.post16 = Post.objects.create(
            author=self.user,
            text='Тестовый тeкст',
            group=self.group,
            image=uploaded,
        )

        obj_index = self.authorized_client.get(
            reverse('posts:index')).context['page_obj'][0]
        obj_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                    )).context['page_obj'][0]
        obj_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user}'}
                    )).context['page_obj'][0]
        obg_post_detail = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.user.posts.all()[0].pk}'}
                    )).context['page_obj']

        templates_reversed_names = {
            # почему-то у первых трёх  не важно какой текст у поста если писать
            # именно текстом, как в 4-й паре ключ-значения
            obj_group: ([self.user, self.post16,
                         self.group, self.post16.image],
                        [obj_group.author, obj_group.text,
                         obj_group.group, obj_group.image]),
            obj_profile: (
                [self.user, self.post16,
                 self.group, self.post16.image],
                [obj_profile.author, obj_profile.text,
                 obj_profile.group, obj_profile.image]),
            obj_index: ([self.user, self.post16,
                         self.group, self.post16.image],
                        [obj_index.author, obj_index.text,
                         obj_index.group, obj_index.image]),
            obg_post_detail: ([self.user, 'Тестовый тeкст',
                               self.group, self.post16.image],
                              [obg_post_detail.author, obg_post_detail.text,
                               obg_post_detail.group, obg_post_detail.image])
        }
        for gived, received in templates_reversed_names.items():
            with self.subTest(gived=gived):
                for increasing_gived, increasing_received in \
                        zip(received[0], received[1]):
                    self.assertEqual(
                        increasing_received, increasing_gived)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('page_obj', context)
            post = context['page_obj']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.user)
        if not self.test_paginator:
            self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)

    def test_index_page_context_is_correct(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)

    def test_profile_page_context_is_correct(self):
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        self.check_context_contains_page_or_post(response.context)
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user)

    def test_post_page_context_is_correct(self):
        response = self.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.pk}'}
                    ))
        self.check_context_contains_page_or_post(response.context, post=True)

    def test_group_page_context_is_correct(self):
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                    ))
        self.check_context_contains_page_or_post(response.context)

    def test_paginator(self):
        Post.objects.bulk_create(
            [Post(author=self.user,
                  text='Тестовый пост',
                  group=self.group,
                  # pub_date=datetime.datetime.now().strftime(
                  #     "%Y-%m-%d %H:%M:%S"
                  )] * 14
        )
        pag_index = reverse('posts:index')
        pag_group = reverse('posts:group_list',
                            kwargs={'slug': f'{self.group.slug}'}
                            )
        urls = [pag_index] * 2 + [pag_group] * 2
        pages = (1, 2)
        posts_on_page = (settings.POSTS_ON_PAGE, settings.POSTS_ON_PAGE * 0.5)

        for url in urls:
            for page, expected_count in zip(pages, posts_on_page):
                with self.subTest(url=url):
                    response = self.client.get(url, {"page": page})
                    self.check_context_contains_page_or_post(
                        response.context
                    )
                    self.assertEqual(
                        len(response.context['page_obj']), expected_count
                    )
                    cache.clear()

    def test_new_post_and_edit_post_pages_context_is_correct(self):
        url_create = reverse('posts:post_create')
        url_edit = reverse('posts:post_edit', kwargs={
            'post_id': f'{self.post.pk}'})
        urls = (url_create, url_edit)
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'],
                                      forms.ModelForm)
                if url == url_create:
                    self.assertFalse(response.context['is_edit'])
                else:
                    self.assertTrue(response.context['is_edit'])

    def test_cache(self):
        # print(cache.cache_page())
        new_post = Post.objects.create(
            author=self.user,
            text='удаляемый Тестовый пост',
        )
        response_before_delete = self.guest_client.get(
            reverse('posts:index', )).content
        Post.objects.get(text='удаляемый Тестовый пост').delete()
        response_after_delete = self.guest_client.get(
            reverse('posts:index', )).content
        self.assertEqual(response_before_delete, response_after_delete)

    def test_follow_unfollow(self):
        checker_follow_unfollow = \
            User.objects.create_user(username='checker')
        authorized_client_checker = Client()
        authorized_client_checker.force_login(checker_follow_unfollow)
        count_follow_objects_before = Follow.objects.count()
        authorized_client_checker.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        count_follow_objects_after_create = Follow.objects.count()
        # сравнение кол-во объектов подписки до(+1) и после создания объекта
        self.assertEqual(count_follow_objects_after_create,
                         count_follow_objects_before + 1)
        checker_follow_index = \
            User.objects.create_user(username='checker_index_follow')
        authorized_client_checker_index_follow = Client()
        authorized_client_checker_index_follow.\
            force_login(checker_follow_index)
        len_follow_index_checker_who_didnt_follow = len(
            authorized_client_checker_index_follow.get(
                reverse('posts:follow_index')).context['page_obj'])
        len_follow_index_checker = len(
            authorized_client_checker.get(
                reverse('posts:follow_index')).context['page_obj'])
        # Проверка, что новая запись пользователя
        # появляется в ленте тех, кто на
        # него подписан и не появляется в ленте тех, кто не подписан.
        self.assertEqual(
            len_follow_index_checker_who_didnt_follow + 1,
            len_follow_index_checker)
        authorized_client_checker.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}))
        count_follow_objects_after_delete = Follow.objects.count()
        # сравнение кол-во объектов подписки до создания
        # и после удаления объекта
        self.assertEqual(count_follow_objects_after_delete,
                         count_follow_objects_before)
