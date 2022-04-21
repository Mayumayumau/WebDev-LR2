from flask import Flask, Blueprint
from flask_restx import Api, Resource, fields, reqparse


app = Flask(__name__)
api = Api(app=app, description='A mini library API', title='Library API')
name_space = api.namespace('Books', description='Books') # http://127.0.0.1:5000/books

books_model = api.model('books', {
    'name': fields.String(required=True, description='Book Name'),
    'author': fields.String(required=True, description='Author Name'),
    'year': fields.Integer(required=False, description='Publishing Year'),
    'pages': fields.Integer(description='Number of Pages'),
    'genre': fields.List(fields.String, description='Book Genre'),
    'rating': fields.Float(description='Goodreads.com rating')
})

books = [
    {'id': 1,'name': 'War and Peace', 'author': 'Leo Tolstoy', 'genre': ['epic', 'classics']},
    {'id': 2,'name': 'Crime and Punishment', 'author': 'Feodor Dostoevsky', 'year': 1853}
]

reqp = reqparse.RequestParser()
reqp.add_argument('name', type=str, required=False)
reqp.add_argument('author', type=str, required=False)
reqp.add_argument('year', type=int, required=False)
reqp.add_argument('pages', type=int, required=False)
reqp.add_argument('genre', type=str, action='append', required=False)
reqp.add_argument('rating', type=float, required=False)

@name_space.route('/')
class BookList(Resource):
    @name_space.marshal_list_with(books_model)
    def get(self):
        """List all books"""
        return books
    @name_space.expect(books_model)
    @name_space.marshal_with(books_model)
    def post(self):
        """Add a book to the list"""
        global books
        args = reqp.parse_args()
        args['id'] = books[-1]['id'] + 1
        books.append(args)

@name_space.route('/<int:id>')
@name_space.param('id', 'A unique identifier')
@name_space.response(404, 'Book not found')
class BookID(Resource):
    @name_space.doc(params={'id': 'A book ID'})
    @name_space.marshal_with(books_model)
    def get(self, id):
        """Show a book info"""
        for book in books:
            if book['id'] == id:
                return book
        name_space.abort(404)

    @name_space.doc(params={'id': 'A book ID'})
    def delete(self, id):
        """Delete a book from the list"""
        for i in range(len(books)):
            if books[i]['id'] == id:
                books.pop(i)
                return f"The book with ID={id} has been deleted"

    # TODO change book info
    @name_space.expect(books_model)
    def put(self, id):
        args = reqp.parse_args()

        for book in books:
           if book['id'] == id:
               for key, value in args.items():
                   if value:
                       book[key] = value

# TODO добавить сортировку по полям, minmax для числовых полей

@name_space.route('/names/<string:name>')
@name_space.param('name', 'A book name')
@name_space.response(404, 'Book not found')
class BookName(Resource):
    @name_space.marshal_with(books_model)
    def get(self, name):
        """Filter books by name"""
        result = []
        for book in books:
            if book['name'].lower() == name.lower():
                result.append(book)
        if result:
            return result
        name_space.abort(404)

@name_space.route('/authors/<string:author>')
@name_space.param('author', 'A book author')
@name_space.response(404, 'Book not found')
class BookAuthor(Resource):
    @name_space.marshal_with(books_model)
    def get(self, author):
        """Filter books by author"""
        result = []
        for book in books:
            if book['author'].lower() == author.lower():
                result.append(book)
        if result:
            return result
        name_space.abort(404)

@name_space.route('/genres/<string:genre>')
@name_space.param('genre', 'A book genre')
@name_space.response(404, 'Book not found')
class BookGenres(Resource):
    @name_space.marshal_with(books_model)
    def get(self, genre):
        """Filter books by genre"""
        result = []
        for book in books:
            genres = book.get('genre')
            if genres and genre.lower() in [el.lower() for el in genres]:
                result.append(book)
        if result:
            return result
        name_space.abort(404)

@name_space.route('/years/<period>')
@name_space.param('period', 'A period of publishing')
@name_space.response(404, 'Book not found')
class PublishingPeriod(Resource):
    @name_space.marshal_with(books_model)
    def get(self, period):
        """Filter books by publishing period"""
        period = [int(el) for el in period.split("-")]
        result = []
        for book in books:
            publishing_year = book.get('year')
            if publishing_year and publishing_year >= period[0] and publishing_year <= period[1]:
                result.append(book)
        if result:
            return result
        name_space.abort(404)

if __name__ == '__main__':
    app.run(debug=True)

