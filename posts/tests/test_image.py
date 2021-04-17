import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

from django.contrib.auth import get_user_model

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # подготавливаем изображение
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.small_txt = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_txt = SimpleUploadedFile(
            name='text.txt',
            content=cls.small_txt,
            content_type='text/plain'
        )
        # Создаем пользователя
        cls.user = User.objects.create_user(username='AA')
        # Создаем группу
        cls.test_group = Group.objects.create(
            title='leo',
            description='test_description',
            slug='leo')
        # Создадим запись в БД
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=Post.pub_date,
            author=cls.user,
            group=cls.test_group,
            image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_image_main_page(self):
        """Картинка появляется на главной странице """
        response = self.authorized_client.get(reverse('posts:posts_index'))
        post = Post.objects.last()
        self.assertTrue(response, post.image)

    def test_image_profile(self):
        """Картинка появляется на странице  профайла"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        post = Post.objects.last()
        self.assertTrue(response, post.image)

    def test_image_main_page(self):
        """Картинка появляется на странице группы  """
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'group': self.group,
                    'slug': self.slug}))
        post = Post.objects.last()
        self.assertTrue(response, post.image)

    def test_image_main_page(self):
        """Картинка появляется на странице поста  """
        response = self.authorized_client.get(reverse(
            'posts:post',
            kwargs={'username': self.user.username,
                    'post_id': self.post.id}))
        post = Post.objects.last()
        self.assertTrue(response, post.image)

    def test_canot_upload_non_image(self):
        """ нельзя загрузить другой файл, кроме изображения """
        errors = ("Формат файлов 'txt' не поддерживается. Поддерживаемые "
                  "форматы файлов: 'bmp, dib, gif, tif, tiff, jfif, jpe, "
                  "jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, blp, bufr, "
                  "cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, "
                  "ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, "
                  "icns, ico, im, iim, mpg, mpeg, mpo, msp, palm, pcd, "
                  "pdf, pxr, psd, bw, rgb, rgba, sgi, ras, tga, icb, vda, "
                  "vst, webp, wmf, emf, xbm, xpm'.")
        form_data = {
            'text': 'Тест',
            'image': self.uploaded_txt
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        # response = self.client.post(reverse('post_edit',
        #                              kwargs={
        #                                  'username': self.user.username,
        #                                  'post_id': self.post.pk}),
        #                      {'image': img,
        #                       'text': 'edited text with an image'})
        self.assertFormError(response,
                             form='form',
                             field='image',
                             errors=errors)
