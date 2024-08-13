from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = slugify(NOTE_TITLE)

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG}
        cls.url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        """Анонимный юзер не может создать заметку."""

        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_note(self):
        """Авторизованный юзер может создать заметку."""

        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_not_unique_slug(self):
        """Тест на уникальность slug"""

        note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.user
        )
        not_unique_slug = {'slug': note.slug}
        response = self.auth_client.post(
            self.url,
            data=not_unique_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_auto_create_slugify_slug(self):
        """Slug формируется автоматически."""

        note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user
        )
        note_slug = note.slug
        self.assertEqual(note_slug, slugify(note.title))


class TestNoteEditeDelete(TestCase):
    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='User'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.another_user = User.objects.create(
            username='AnotherUser'
        )
        cls.another_auth_client = Client()
        cls.another_auth_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.user
        )
        url_arg = (cls.note.slug,)
        cls.note_edit_url = reverse('notes:edit', args=url_arg)
        cls.note_delete_url = reverse('notes:delete', args=url_arg)
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug}

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""

        response = self.auth_client.delete(self.note_delete_url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_author_can_edit_note(self):
        """Автор может изменить свою заметку."""

        response = self.auth_client.post(
            self.note_edit_url,
            data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        """Другой пользователь не может удалить чужую заметку."""

        response = self.another_auth_client.delete(self.note_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_cant_edit_note_of_another_user(self):
        """Другой пользователь не может изменить чужую заметку."""

        response = self.another_auth_client.post(
            self.note_edit_url,
            data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
