from flask import Flask, Blueprint
from flask_restx import Api, Resource, fields


app = Flask(__name__)
api = Api(app=app, description='A mini library API', title='Library API')
name_space = api.namespace('Books', description='Books') # http://127.0.0.1:5000/books

books_model = api.model('books', {
    'name': fields.String(required=True, description='Book Name'),
    'author': fields.String(required=True, description='Author Name'),
    'year': fields.String(required=False, description='Publishing Year'),
    'pages': fields.Integer(description='Number of Pages'),
    'genre': fields.List(fields.String, description='Book Genre'),
    'rating': fields.Float(description='Goodreads.com rating')
})

books = [
    {'name': 'War and Peace', 'author': 'Leo Tolstoy'},
    {'name': 'Crime and Punishment', 'author': 'Feodor Dostoevsky'}
]

@name_space.route('/')
class BookList(Resource):
    @api.marshal_with(books_model)
    def get(self):
        """List all books"""
        return books

if __name__ == '__main__':
    app.run(debug=True)

