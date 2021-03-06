from pydoc import HTMLRepr
from unittest import TestCase

from app import app, db
from models import DEFAULT_IMAGE_URL, User, Post

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly_test"


app.config['TESTING'] = True


app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.create_all()

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

        test_user = User(first_name="test_first",
                        last_name="test_last",
                        image_url=None)

        second_user = User(first_name="test_first_two", 
                        last_name="test_last_two",
                        image_url=None)

        db.session.add_all([test_user, second_user])
        db.session.commit()

        self.user_id = test_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        """Test that user list shows up with users from database"""
        
        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_first", html)
            self.assertIn("test_last", html)

    def test_new_user_form(self):
        """Test that new user form shows up"""

        with self.client as c:
            resp = c.get("/users/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form class="new-user-form', html)


    def test_new_user_submit(self):
        """Test that new user is added to db and page redirects"""

        with self.client as c:
            resp = c.post("/users/new", data = {"first-name": "Jon",
                                                "last-name": "Snow"},
                                        follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Jon", html)

    def test_show_detail_page(self):
        """Test that user detail page shows up"""

        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_first", html)



class PostViewTestCase(TestCase):
    """Test views for posts."""

    def setUp(self):
        """Create test client, add sample data."""

        Post.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_user = User(first_name="test_first",
                        last_name="test_last",
                        image_url=None)

        test_post = Post(title="test_post",
                        content="test content here",
                        user_id=test_user.id)

        db.session.add(test_user)
        db.session.add(test_post)

        db.session.commit()

        self.post_id = test_post.id
        self.user_id = test_user.id
        self.image_url = test_user.image_url

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_new_post_form(self):
        """ Test new post form is loaded """

        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form class="new-post-form', html)


    def test_adding_new_post(self):
        """ Test new post is created and redirects to user detail page """

        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/posts/new",
                                data = {"title": "Coding Rocks",
                                        "content": "I love coding"},
                                follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<img src="{self.image_url}', html)
            self.assertIn("Coding Rocks", html)

    def test_post_detail_page(self):
        """ Test that post detail page shows up """

        with self.client as c:
            resp = c.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test content here", html)

    def test_edit_post(self):
        """ Test edit post functionality and redirect"""

        with self.client as c:
            resp = c.post(f"/posts/{self.post_id}/edit",
                                data = {"title-edit": "I love to code",
                                        "content-edit": "Isn't it the best"},
                                follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("By, ", html)
            self.assertIn("it the best", html)
            self.assertNotIn("test content here", html) #old content