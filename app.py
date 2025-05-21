from flask import Flask, request, render_template, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import User, Movie, db
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_file = os.path.join(basedir, 'instance', 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)


@app.route('/')
def home():
    """This method displays the homepage."""
    return render_template('home.html')


@app.route('/users')
def list_users():
    """This method shows a list of all users."""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_movies.html', user=user, movies=user.movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """This method adds a new user to the database."""
    if request.method == 'POST':
        name = request.form['name']
        try:
            user = User(name=name)
            data_manager.add_user(user)
            return redirect(url_for('user_movies', user_id=user.id))
        except Exception as e:
            print(f"Failed to add user: {e}")

    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """This method adds a movie to a user's movie list."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form['year']
        rating = request.form['rating']

        try:
            movie = Movie(
                title=title,
                director=director,
                year=int(year),
                rating=float(rating),
                user_id=user_id
            )
            data_manager.add_movie(movie)
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            print(f"Failed to add movie: {e}")
            return render_template('message.html', message="Failed to add movie.", user_id=user_id)

    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """This method updates the rating of an existing movie for a given user."""
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        try:
            new_rating = request.form.get('rating')
            movie.rating = float(new_rating)
            data_manager.update_movie(movie)
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            print(f"Error updating movie rating: {e}")
            return render_template('message.html', message="Failed to update rating.")

    return render_template('update_movie.html', movie=movie, user_id=user_id)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()

    if movie:
        try:
            db.session.delete(movie)
            db.session.commit()
            return render_template('message.html', message=f"Movie {movie.title} deleted for user {user_id}!",
                                   user_id=user_id)
        except Exception as e:
            db.session.rollback()
            return render_template('message.html', message="Failed to delete movie.: {e}", user_id=user_id)
    else:
        return render_template('message.html', message="Movie not found.", user_id=user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
