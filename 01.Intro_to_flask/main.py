from flask import Flask, render_template
from flask_restful import Api, Resource

app = Flask(__name__)

# special for rest app
api = Api(app)


class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def serialize(self):
        return self.__dict__


books = []
for i in range(5):
    books.append(Book(f"Title {i}", f"Author {i}"))


class Books(Resource):
    def get(self):
        return [b.serialize() for b in books]


api.add_resource(Books, '/books')


@app.route("/")
def hello():
    return "<h1>Hello Flask!</h1>"


@app.route("/asd")
def hello_from_template():
    context = {"name": "Flask"}
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run()
