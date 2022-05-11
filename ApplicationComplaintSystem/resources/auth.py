from flask_restful import Resource
from flask import request
from decouple import config

from managers.user import UserManager
from managers.auth import AuthManager
from utils.decorators import validate_schema
from schemas.request.user import (
    ComplainerRegisterRequestSchema,
    ComplainerLoginRequestSchema,
)


class Register(Resource):
    @validate_schema(ComplainerRegisterRequestSchema)
    def post(self):
        user = UserManager.register(request.get_json())
        token = AuthManager.encode_token(user)
        return {'token': token}, 201


class Login(Resource):
    @validate_schema(ComplainerLoginRequestSchema)
    def post(self):
        user = UserManager.login(request.get_json())
        token = AuthManager.encode_token(user)
        return {'token': token}, 200




