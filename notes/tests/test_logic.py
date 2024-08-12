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
        cls.user = User.objects.create(username='author')
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
            author_id=self.user.id
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


# class TestNoteEditeDelete(TestCase):

