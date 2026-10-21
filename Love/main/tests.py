from datetime import date
from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse
from PIL import Image

from .models import BucketItem, Moment


class FrontendViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test-user',
            password='StrongPass!2026',
        )

    def test_private_pages_redirect_to_login(self):
        for url_name in (
            'moments_list',
            'bucket_list',
            'random_moment',
            'comic_story',
        ):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertRedirects(
                    response,
                    f'{reverse("login")}?next={reverse(url_name)}',
                )

    def test_comic_page_renders_existing_template(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('comic_story'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comix.html')
        self.assertContains(response, 'Як усе починалося')
        self.assertContains(response, reverse('comic_story'))

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Увійти')
        self.assertContains(response, 'Створити акаунт')
        self.assertNotContains(response, 'secret_code')

    def test_bucket_page_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bucket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Додати')

    def test_register_creates_user_and_signs_them_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new-user',
                'password': 'StrongPass!2026',
                'password_confirmation': 'StrongPass!2026',
            },
        )
        self.assertRedirects(response, reverse('moments_list'))
        self.assertTrue(
            self.client.session.get('_auth_user_id')
        )
        self.assertTrue(get_user_model().objects.filter(username='new-user').exists())

    def test_existing_user_can_sign_in(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'test-user',
                'password': 'StrongPass!2026',
            },
        )
        self.assertRedirects(response, reverse('moments_list'))
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new-user',
                'password': 'StrongPass!2026',
                'password_confirmation': 'DifferentPass!2026',
            },
            follow=True,
        )

        self.assertContains(response, 'Паролі не збігаються.')
        self.assertFalse(get_user_model().objects.filter(username='new-user').exists())

    def test_moments_are_filtered_by_period_and_category(self):
        matching = Moment.objects.create(
            title='Романтичний спогад',
            description='Опис',
            date=date(2026, 1, 1),
            period='3-6',
            category='romantic',
        )
        Moment.objects.create(
            title='Інший спогад',
            description='Опис',
            date=date(2026, 1, 2),
            period='0-3',
            category='funny',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('moments_list'),
            {'period': '3-6', 'category': 'romantic'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['moments']), [matching])

    def test_all_periods_filter_returns_all_moments_in_selected_category(self):
        funny_early = Moment.objects.create(
            title='Смішний ранній момент',
            description='Опис',
            date=date(2025, 1, 1),
            period='0-3',
            category='funny',
        )
        funny_later = Moment.objects.create(
            title='Смішний пізній момент',
            description='Опис',
            date=date(2026, 1, 1),
            period='1plus',
            category='funny',
        )
        Moment.objects.create(
            title='Романтичний момент',
            description='Опис',
            date=date(2026, 2, 1),
            period='1plus',
            category='romantic',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('moments_list'),
            {'period': 'all', 'category': 'funny'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context['moments']),
            {funny_early, funny_later},
        )
        self.assertContains(response, 'Усі періоди')

    def test_moment_list_displays_full_photo_in_card(self):
        moment = Moment.objects.create(
            title='Спогад із фото',
            description='Опис',
            date=date(2026, 1, 1),
            image='moments_photos/photo.jpg',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('moments_list'),
            {'period': 'all', 'category': 'all'},
        )

        self.assertContains(response, moment.image.url)
        self.assertContains(response, 'object-contain')

    def test_moment_list_shows_summary_and_detail_page_shows_full_content(self):
        moment = Moment.objects.create(
            title='Наша прогулянка',
            description='Довгий опис особливого дня',
            date=date(2026, 1, 1),
            period='3-6',
            category='romantic',
            location='Біля річки',
        )
        self.client.force_login(self.user)

        list_response = self.client.get(
            reverse('moments_list'),
            {'period': '3-6', 'category': 'all'},
        )
        self.assertContains(list_response, moment.title)
        self.assertContains(list_response, 'романтично')
        self.assertContains(list_response, 'Читати більше')
        self.assertNotContains(list_response, moment.description)
        self.assertNotContains(list_response, moment.location)

        detail_response = self.client.get(
            reverse('moment_detail', args=[moment.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, moment.title)
        self.assertContains(detail_response, moment.description)
        self.assertContains(detail_response, moment.location)
        self.assertContains(detail_response, '3–6 місяців')

    def test_moment_detail_requires_login_and_returns_404_for_unknown_id(self):
        moment = Moment.objects.create(
            title='Приватний спогад',
            description='Опис',
            date=date(2026, 1, 1),
        )

        response = self.client.get(reverse('moment_detail', args=[moment.pk]))
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("moment_detail", args=[moment.pk])}',
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('moment_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_moment_form_is_displayed_and_creates_moment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('moments_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Додати спогад')
        self.assertNotContains(response, 'name="description"')

        response = self.client.get(reverse('moment_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Додати новий спогад')

        response = self.client.post(
            reverse('moment_create'),
            {
                'title': 'Наша прогулянка',
                'description': 'Гуляли біля річки',
                'date': '2026-10-18',
                'period': '3-6',
                'category': 'romantic',
                'location': 'Біля річки',
            },
        )

        moment = Moment.objects.get()
        self.assertEqual(moment.title, 'Наша прогулянка')
        self.assertRedirects(response, reverse('moment_detail', args=[moment.pk]))

    def test_moment_form_accepts_multiple_optional_gallery_photos(self):
        self.client.force_login(self.user)

        def create_image_upload(name):
            image_bytes = BytesIO()
            Image.new('RGB', (2, 2), color='red').save(image_bytes, format='PNG')
            return SimpleUploadedFile(
                name,
                image_bytes.getvalue(),
                content_type='image/png',
            )

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse('moment_create'),
                    {
                        'title': 'Наш день',
                        'description': 'Гарний спогад',
                        'date': '2026-10-18',
                        'period': '3-6',
                        'category': 'romantic',
                        'additional_images': [
                            create_image_upload('photo-one.png'),
                            create_image_upload('photo-two.png'),
                        ],
                    },
                )

                moment = Moment.objects.get()
                self.assertRedirects(
                    response,
                    reverse('moment_detail', args=[moment.pk]),
                )
                self.assertEqual(moment.photos.count(), 2)

                detail_response = self.client.get(
                    reverse('moment_detail', args=[moment.pk])
                )
                self.assertContains(detail_response, 'Фото спогаду')
                self.assertContains(detail_response, 'gallery/photo-one.png')
                self.assertContains(detail_response, 'gallery/photo-two.png')

    def test_invalid_moment_form_shows_errors_without_creating_record(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('moment_create'),
            {
                'title': '',
                'description': 'Без назви',
                'date': '2026-10-18',
                'period': '3-6',
                'category': 'romantic',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms.html')
        self.assertContains(response, 'Це поле обов’язкове.')
        self.assertEqual(Moment.objects.count(), 0)

    def test_bucket_ideas_remain_separate_from_moments(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_bucket_item'),
            {'title': '  Пікнік  '},
        )
        self.assertRedirects(response, reverse('bucket_list'))
        item = BucketItem.objects.get()
        self.assertEqual(item.title, 'Пікнік')
        self.assertEqual(Moment.objects.count(), 0)

        response = self.client.get(reverse('bucket_list'))
        self.assertContains(response, 'Нова ідея для побачення')
        self.assertContains(response, 'Пікнік')

        self.client.post(reverse('toggle_bucket_item', args=[item.pk]))
        item.refresh_from_db()
        self.assertTrue(item.is_completed)
        self.assertEqual(Moment.objects.count(), 0)
        response = self.client.get(reverse('moments_list'))
        self.assertEqual(list(response.context['moments']), [])

        with self.assertRaises(NoReverseMatch):
            reverse('convert_to_moment', args=[item.pk])

    def test_random_moment_page_handles_empty_and_existing_database(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('random_moment'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['random_moment'])

        moment = Moment.objects.create(
            title='Несподіваний спогад',
            description='Опис',
            date=date(2026, 1, 1),
        )
        response = self.client.get(reverse('random_moment'))
        self.assertEqual(response.context['random_moment'], moment)
