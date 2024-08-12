from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm, WARNING
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
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author_id=cls.user.id
        )
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_anonymous_user_cant_create_note(self):
        """Анонимный юзер не может создать заметку."""

        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auth_user_can_create_note(self):
        """Авторизованный юзер может создать заметку."""

        self.auth_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    # def test_auth_user_can_edit_notes(self):
    #     """Автор может редактировать заметку."""
    #     # Выполняем запрос на редактирование от имени автора комментария.
    #     response = self.author_client.post(self.edit_url, data=self.form_data)
    #     # Проверяем, что сработал редирект.
    #     self.assertRedirects(response, self.url_to_comments)
    #     # Обновляем объект комментария.
    #     self.comment.refresh_from_db()
    #     # Проверяем, что текст комментария соответствует обновленному.
    #     self.assertEqual(self.comment.text, self.NEW_COMMENT_TEXT)

    def test_not_unique_slug(self):
        """Тест на уникальность slug"""

        not_unique_slug = {'slug': self.note.slug}
        response = self.auth_client.post(self.add_url, data=not_unique_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
