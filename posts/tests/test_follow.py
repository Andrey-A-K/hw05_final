from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='AA',
                                            password=11)
        # и 2го, для проверки подписки
        cls.user_2 = User.objects.create_user(username='BB',
                                              password=22)
        # Создаем группу
        cls.test_group = Group.objects.create(title='leo', slug='leo')
        # Создадим запись в БД
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=Post.pub_date,
            author=cls.user,
            group=cls.test_group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # И еще один, для проверки подписок
        self.authorized_client_2 = Client()
        # Авторизуем пользователей
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    def test_follow(self):
        """ Проверяется, что после подписки появится новый обект Follow"""
        follow = reverse('posts:profile_follow',
                         kwargs={'username': self.user_2.username})
        self.authorized_client.get(follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """ а после отписки он исчезнет """
        unfollow = reverse('posts:profile_unfollow',
                           kwargs={'username': self.user_2.username})
        self.authorized_client.get(unfollow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_authorized_user_comment_posts(self):
        """авторизированный пользователь может комментировать посты"""
        response = self.authorized_client.get(
            reverse('posts:add_comment',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }))
        self.assertEqual(response.status_code, 200)

    def test_authorized_user_create_comment(self):
        """комментарий, оставленный авторизированным юзером
           появляется на странице поста"""
        comment = reverse('posts:add_comment',
                          kwargs={'username': self.post.author.username,
                                  'post_id': self.post.id})
        response = self.authorized_client.post(
            comment, {'text': 'Comment 1'},
            follow=True)
        self.assertContains(response, 'Comment 1')

    def test_unauthorized_user_comment_posts(self):
        """неавторизированный пользователь не может
            зайти на страницу комментариев"""
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }))
        self.assertEqual(response.status_code, 302)

    def test_new_entry_in_subscriptions(self):
        """Новая запись автора появляется в ленте тех,
           кто на него подписан и не появляется в профиле
           неподписавшихся на автора"""
        # подписываем user на user_2
        follow = reverse('posts:profile_follow',
                         kwargs={'username': self.user_2.username})
        self.authorized_client.get(follow, follow=True)
        # добавляем новую запись от имени user_2
        self.post = Post.objects.create(text='подписка', author=self.user_2)
        # делаем запрос на страницу подписки с профиля подписанного юзера
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['post_list'])
        # делаем запрос на страницу подписки с профиля неподписанного юзера
        response2 = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response2.context['post_list'])
