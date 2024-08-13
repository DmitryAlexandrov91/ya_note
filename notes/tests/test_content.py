from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNotesList(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.reader = User.objects.create(
            username='Другой пользователь'
        )
        Note.objects.bulk_create(
            [Note(
                title=f'заметка{index}',
                text='Текст заметки.',
                author=cls.author,
                slug=str(index)
                )
                for index in range(5)]
            )
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)

    def test_only_author_notes(self):
        """Проверка на отображение только заметок автора."""

        # Создаём тестовую заметку от другого user'a
        Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            author=self.reader,
            slug='zametka'
            )
        response = self.user_client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        author_notes_list = Note.objects.filter(
            author_id=self.author.id
        )
        self.assertQuerysetEqual(author_notes_list, object_list, ordered=False)

    def test_news_order(self):
        """Сортировка заметок на странице по ID."""

        responce = self.user_client.get(self.NOTES_URL)
        object_list = responce.context['object_list']
        author_notes = [note.id for note in object_list]
        sorted_dates = sorted(author_notes)
        self.assertEqual(author_notes, sorted_dates)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы на странице создания заметки."""

        response = self.user_client.get(
            reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
