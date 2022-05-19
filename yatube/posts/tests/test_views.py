from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_name')

        cls.group = Group.objects.create(
                title='Заголовок для тестовой группы',
                slug='test_slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания поста',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostTests.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test_name'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        index_group_profile_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in index_group_profile_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                first_object = response.context["page_obj"][0]
                post_text = first_object.text
                post_author = first_object.author
                post_group = first_object.group
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_author, self.post.author)
                self.assertEqual(post_group.title, self.post.group.title)
                self.assertEqual(post_group.slug, self.post.group.slug)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        first_object = response.context["post"]
        post_text = first_object.text
        post_author = first_object.author
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)

    def test_post_form_show_correct_context(self):
        """Шаблон post_create/post_edit сформирован
        с правильным контекстом."""
        create_edit_pages = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        ]
        for page in create_edit_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        self.assertIn('form', response.context)
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_get_right_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context["page_obj"][0]
        post_text = first_object.text
        self.assertTrue(post_text, 'Тестовая запись для создания поста')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(settings.POSTS_FOR_ONE_PAGE + 1):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

        cls.list_urls = {
            reverse("posts:index"): "index",
            reverse(
                "posts:group_list", kwargs={"slug": "test_slug2"}
            ): "group",
            reverse(
                "posts:profile",
                kwargs={"username": "test_name"}
            ): "profile",
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        for tested_url in self.list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                settings.POSTS_FOR_ONE_PAGE
            )

    def test_second_page_contains_other_posts(self):
        for tested_url in self.list_urls.keys():
            response = self.client.get(tested_url + "?page=2")
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 1
            )
