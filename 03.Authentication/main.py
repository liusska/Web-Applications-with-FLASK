import enum
import jwt

from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from marshmallow_enum import EnumField
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)

db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_port = config('DB_PORT')
db_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@localhost:{db_port}/{db_name}'
db = SQLAlchemy(app)
api = Api(app)
migrate = Migrate(app, db)

auth = HTTPTokenAuth(scheme='Bearer')


def permission_required(permission):
    def wrapper(func):
        def decorated_functon(*args, **kwargs):
            if user.role == permission:
                return func(*args, **kwargs)
            raise Forbidden('You have no access to this resource')
        return decorated_functon
    return wrapper


def validate_data(schema_name):
    def wrapper(func):
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            schema = schema_name()
            errors = schema.validate(data)
            if errors:
                raise BadRequest(f'Invalid data fields - {", ".join(errors)}')
            return func(*args, **kwargs)
        return decorated_function
    return wrapper



@auth.verify_token
def verify_token(token):
    try:
        user_id = User.decode_token(token)
        return User.query.filter_by(id=user_id).first()
    except Exception as ex:
        raise ex


class UserRoleEnum(enum.Enum):
    super_admin = 'super admin'
    admin = 'admin'
    user = 'user'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Text)
    role = db.Column(db.Enum(UserRoleEnum), default=UserRoleEnum.user)
    created_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())

    def encode_token(self):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=2),
            'sub': self.id
        }

        return jwt.encode(payload, key=config("JWT_KEY"), algorithm='HS256')

    @staticmethod
    def decode_token(token):
        try:
            data = jwt.decode(token, key=config("JWT_KEY"), algorithms=["HS256"])
            return data["sub"]
        except jwt.InvalidTokenError:
            raise BadRequest("Invalid token")
        except jwt.ExpiredSignatureError:
            raise BadRequest("Token expired")


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xll = "xll"


class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(
        db.Enum(ColorEnum),
        default=ColorEnum.white,
        nullable=False
    )
    size = db.Column(
        db.Enum(SizeEnum),
        default=SizeEnum.s,
        nullable=False
    )
    photo = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


def validate_full_name(value):
    try:
        first_name, last_name = value.split()
    except:
        raise ValidationError("Full name should contain first name and last name")


class UserSignUpSchema(Schema):
    email = fields.Email()
    password = fields.String()
    full_name = fields.String(
        required=True,
        # if is just one check
        # validate=validate.Length(min=2, max=255)
        validate=validate.And(validate.Length(min=2, max=255), validate_full_name)
    )


class SignUp(Resource):
    @validate_data(UserSignUpSchema)
    def post(self):
        data = request.get_json()
        try:
            data["password"] = generate_password_hash(password=data['password'], method='sha256')
            user = User(**data)
            db.session.add(user)
            db.session.commit()
        except Exception as ex:
            if "UniqueViolation" in str(ex):
                raise BadRequest("This email is already in use")
            raise BadRequest("invalid data")
        token = user.encode_token()
        return {"token": token}, 201


class ClothesOutSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    color = EnumField(ColorEnum)
    size = EnumField(SizeEnum)
    foto = fields.String()
    created_on = fields.DateTime()
    updated_now = fields.DateTime()


class ClothesResource(Resource):
    @auth.login_required
    @permission_required(UserRoleEnum.admin)
    def get(self):
        # user = auth.current_user()
        clothes = Clothes.query.all()
        schema = ClothesOutSchema()
        clothes = schema.dump(clothes, many=True)
        return {'clothes': clothes}


api.add_resource(SignUp, '/register')
api.add_resource(ClothesResource, '/clothes')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)



