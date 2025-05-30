from flask import Flask, request, render_template, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import User, Movie, db
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db.init_app(app)

load_dotenv()

data_manager = SQLiteDataManager(app)


@app.route('/')
def home():
    """This method displays the homepage."""
    return render_template('home.html')


@app.route('/users')
def list_users():
    """This method shows a list of all users."""
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return render_template("message.html", message="Failed to load users.")


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """This method fetches and displays the list of movies for a given user."""
    try:
        user = User.query.get_or_404(user_id)
        return render_template('user_movies.html', user=user, movies=user.movies)
    except Exception as e:
        print(f"Error fetching user or movies: {e}")
        return render_template("message.html", message="Unable to load user or movies.")


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
            return render_template('message.html', message="Failed to add user.")
    return render_template('add_user.html')


@app.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """This method deletes a user and all their associated movies."""
    try:
        user = User.query.get(user_id)
        if user:
            user_name = user.name
            db.session.delete(user)
            db.session.commit()
            return render_template(
                "message.html",
                message=f"User {user_name} was successfully deleted.",
                redirect_to='users'
            )
        else:
            return render_template(
                "message.html",
                message="User not found.",
                redirect_to='users'
            )
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        return render_template(
            "message.html",
            message="Failed to delete user.",
            redirect_to='users'
        )


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """This method adds a movie to a user's movie list using the OMDb API."""
    user = User.query.get_or_404(user_id)
    api_key = os.getenv("API_KEY")

    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating']

        api_url = "http://www.omdbapi.com/"
        params = {
            "t": title,
            "apikey": api_key
        }

        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                try:
                    movie = Movie(
                        title=data.get("Title", title),
                        director=data.get("Director", "Unknown"),
                        year=int(data.get("Year", 0)),
                        rating=float(rating),
                        poster=data.get("Poster"),
                        user_id=user_id
                    )
                    data_manager.add_movie(movie)
                    return redirect(url_for('user_movies', user_id=user_id))
                except Exception as e:
                    print(f"Error saving movie: {e}")
                    return render_template('message.html', message="Failed to save movie.", user_id=user_id)
            else:
                return render_template('message.html', message="Movie not found in OMDb API.", user_id=user_id)
        else:
            return render_template('message.html', message="Error connecting to OMDb API.", user_id=user_id)

    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """This method updates the rating of an existing movie for a given user."""
    user = User.query.get_or_404(user_id)
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        try:
            new_title = request.form.get("title")
            new_rating = request.form.get("rating")

            if new_title:
                movie.title = new_title
            if new_rating:
                movie.rating = float(new_rating)

            db.session.commit()
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating movie rating: {e}")
            return render_template('message.html', message="Failed to update rating.", user_id=user_id)

    return render_template('update_movie.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """This method deletes a movie from a user's movie list."""
    try:
        user = User.query.get(user_id)
        movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
        if user and movie:
            user_name = user.name
            db.session.delete(movie)
            db.session.commit()
            return render_template(
                'message.html',
                message=f"Movie {movie.title} deleted for user {user_name}!",
                user_id=user_id
            )
        else:
            return render_template('message.html', message="Movie or user not found.", user_id=user_id)
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting movie: {e}")
        return render_template('message.html', message="Failed to delete movie.", user_id=user_id)


@app.errorhandler(404)
def page_not_found(error):
    """This method displays a 404 Page not Found error page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """This method displays a 500 Internal Server Error error page."""
    return render_template("500.html"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
