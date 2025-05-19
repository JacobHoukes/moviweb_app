from flask import Flask, request, jsonify, render_template_string
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import User, Movie
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_file = os.path.join(basedir, 'instance', 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)


@app.route('/')
def home():
    """This method displays the welcome page."""
    return render_template_string("<h1>Welcome to MovieWeb App 🎬</h1>")


@app.route('/users', methods=['GET'])
def list_users():
    """This method shows a list of all users."""
    users = data_manager.get_all_users()
    users_html = "<ul>"
    for user in users:
        users_html += f"<li>{user.name} (ID: {user.id})</li>"
    users_html += "</ul>"
    return render_template_string("<h1>All Users</h1>" + users_html)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """This method shows all movies for a specific user."""
    movies = data_manager.get_user_movies(user_id)
    movie_list = "<ul>"
    for movie in movies:
        movie_list += f"<li>{movie.title}</li>"
    movie_list += "</ul>"
    return render_template_string(f"<h1>User {user_id}'s Movies</h1>" + movie_list)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """This method adds a new user to the database."""
    if request.method == 'POST':
        name = request.form['name']
        user = User(name=name)
        data_manager.add_user(user)
        return render_template_string("<p>User added!</p>")

    return '''
        <form method="post">
            <label>Name:</label>
            <input name="name" type="text">
            <input type="submit" value="Add User">
        </form>
    '''


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """This method adds a movie to a user's movie list."""
    if request.method == 'POST':
        title = request.form['title']
        movie = Movie(title=title, user_id=user_id)
        data_manager.add_movie(movie)
        return render_template_string("<p>Movie added!</p>")

    return f'''
        <form method="post">
            <label>Movie Title:</label>
            <input name="title" type="text">
            <input type="submit" value="Add Movie for User {user_id}">
        </form>
    '''


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """This method updates the title of a specific movie."""

    if request.method == 'POST':
        title = request.form['title']
        movie = Movie(id=movie_id, title=title, user_id=user_id)
        data_manager.update_movie(movie)
        return render_template_string("<p>Movie updated!</p>")

    return f'''
        <form method="post">
            <label>New Movie Title:</label>
            <input name="title" type="text">
            <input type="submit" value="Update Movie {movie_id} for User {user_id}">
        </form>
    '''


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie_route(user_id, movie_id):
    """This method deletes a specific movie from a user's list."""
    data_manager.delete_movie(movie_id)
    return render_template_string(f"<p>Movie {movie_id} deleted for User {user_id}!</p>")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
