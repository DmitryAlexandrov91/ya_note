from http import HTTPStatus


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.reader = User.objects.create(
            username='Другой пользователь'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
            )

    def test_note_create(self):
        """Создание заметки."""

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_pages_for_guest_availability(self):
        """Доступ незалогиненному юзеру."""

        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                responce = self.client.get(url)
                self.assertEqual(
                    responce.status_code,
                    HTTPStatus.OK,
                    )

    def test_redirect_for_anonymous_client(self):
        """Редирект незалогинненого юзера."""

        login_url = reverse('users:login')
        slug = (self.note.slug,)
        not_for_guest_urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug), 
        )
        for name, args in not_for_guest_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                responce = self.client.get(url)
                self.assertRedirects(responce, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        """Страница заметки, удаления и редактирования только автору."""

        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:delete', 'notes:edit'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    responce = self.client.get(url)
                    self.assertEqual(
                        responce.status_code, status)
