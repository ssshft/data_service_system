from flask_login import UserMixin


class User(UserMixin):
    pass


users = [
    {'id': 'rad', 'username': 'rad', 'password': 'rad_123456'}
]


def query_user(user_id):
    for user in users:
        if user_id == user['id']:
            return user
