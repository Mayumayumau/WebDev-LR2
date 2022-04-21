from flask import Flask, Blueprint
from flask_restx import Api, Resource, fields, reqparse
from numpy import inf

app = Flask(__name__)
api = Api(app=app, description='A mini library API', title='Library API')
name_space = api.namespace('Books', description='Books')  # http://127.0.0.1:5000/books

books_model = api.model('books', {
    'name': fields.String(required=True, description='Book Name'),
    'author': fields.String(required=True, description='Author Name'),
    'year': fields.Integer(required=False, description='Publishing Year'),
    'pages': fields.Integer(description='Number of Pages'),
    'genre': fields.List(fields.String, description='Book Genre'),
    'rating': fields.Float(description='Goodreads.com rating')
})

books = [
    {'book_id': 1, 'name': 'War and Peace', 'author': 'Leo Tolstoy', 'genre': ['epic', 'classics'], 'rating': 4.3},
    {'book_id': 2, 'name': 'Crime and Punishment', 'author': 'Feodor Dostoevsky', 'year': 1853, 'rating': 4.7, 'pages': 345}
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
        args['book_id'] = books[-1]['book_id'] + 1
        books.append(args)


@name_space.route('/<int:book_id>')
@name_space.param('book_id', 'A unique identifier')
@name_space.response(404, 'Book not found')
class BookID(Resource):
    @name_space.doc(params={'book_id': 'A book ID'})
    @name_space.marshal_with(books_model)
    def get(self, book_id):
        """Show a book info"""
        for book in books:
            if book['book_id'] == book_id:
                return book
        name_space.abort(404)

    @name_space.doc(params={'book_id': 'A book ID'})
    def delete(self, book_id):
        """Delete a book from the list"""
        for i in range(len(books)):
            if books[i]['book_id'] == book_id:
                books.pop(i)
                return f"The book with ID={book_id} has been deleted"

    # TODO change book info
    @name_space.expect(books_model)
    def put(self, book_id):
        args = reqp.parse_args()
        for book in books:
            if book['book_id'] == book_id:
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


def find_books(limits, field):
    limits = [int(el) for el in limits.split("-")]
    result = []
    for book in books:
        data = book.get(field)
        if data and limits[0] <= data <= limits[1]:
            result.append(book)
    return result


@name_space.route('/years/<period>')
@name_space.param('period', 'A period of publishing')
@name_space.response(404, 'Book not found')
class PublishingPeriod(Resource):
    @name_space.marshal_with(books_model)
    def get(self, period):
        """Filter books by publishing period"""
        result = find_books(period, 'year')
        print(result)
        if result:
            return result

        name_space.abort(404)


@name_space.route('/pages/<limits>')
@name_space.param('limits', 'Limits for the page amount')
@name_space.response(404, 'Book not found')
class PageAmount(Resource):
    @name_space.marshal_with(books_model)
    def get(self, limits):
        """Filter books by page amount"""
        result = find_books(limits, 'pages')
        if result:
            return result
        name_space.abort(404)


@name_space.route('/ratings/<limits>')
@name_space.param('limits', 'Limits for the rating')
@name_space.response(404, 'Book not found')
class BookRating(Resource):
    @name_space.marshal_with(books_model)
    def get(self, limits):
        """Filter books by page amount"""
        result = find_books(limits, 'rating')
        if result:
            return result
        name_space.abort(404)


stats_model = api.model('stats', {
    'min': fields.Nested(books_model, required=True, description='The lowest value in the library'),
    'max': fields.Nested(books_model, required=True, description='The highest value in the library'),
    'average': fields.Raw(required=True, description='The average value')
})


@name_space.route('/stats/<arg>')
@name_space.param('arg', 'The field to evaluate')
class LibStats(Resource):
    @name_space.marshal_with(stats_model)
    def get(self, arg):
        """Show library statistics by a number field"""
        result = {'min': None, 'max': None, 'average': None}
        min_value = inf
        max_value = 0
        average_value = 0
        num = 0
        for book in books:
            value = book.get(arg)
            if value:
                if value < min_value:
                    result['min'] = book
                    min_value = value
                elif value > max_value:
                    result['max'] = book
                    max_value = value
                average_value += value
                num += 1
        average_value /= num
        if average_value > 0:
            if arg == 'year':
                average_value = int(average_value)
            result['average'] = average_value
        return result


if __name__ == '__main__':
    app.run(debug=True)
