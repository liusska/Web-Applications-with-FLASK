from db import db

from models.users import ComplainerModel
from werkzeug.security import generate_password_hash


class UserManager:
    @staticmethod
    def register(user_data):
        user_data['password'] = generate_password_hash(data['password'])
        user = ComplainerModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return user