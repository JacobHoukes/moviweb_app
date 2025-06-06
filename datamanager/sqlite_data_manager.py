from models import db, User, Movie
from datamanager.data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        """This method connects SQLAlchemy to the Flask app and creates tables."""
        self.app = app
        with app.app_context():
            db.create_all()

    def get_all_users(self):
        """This method gets a list of all users in the database."""
        return User.query.all()

    def get_user_movies(self, user_id):
        """This method gets all movies that belong to a specific user."""
        return Movie.query.filter_by(user_id=user_id).all()

    def add_user(self, user):
        """This method adds a new user to the database."""
        try:
            db.session.add(user)
            db.session.commit()
            print(f"User '{user.name}' added successfully!")
        except Exception as e:
            # undoes any changes made during the current database session if something goes wrong
            db.session.rollback()
            print(f"This method failed to add user: {str(e)}")

    def add_movie(self, movie):
        """This method adds a new movie to the database."""
        try:
            db.session.add(movie)
            db.session.commit()
            print(f"Movie '{movie.title}' added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"This method failed to add movie: {str(e)}")

    def update_movie(self, movie):
        """This method updates the rating of a specific movie."""
        existing = Movie.query.get_or_404(movie.id)
        existing.title = movie.title
        existing.director = movie.director
        existing.year = movie.year
        existing.rating = movie.rating
        db.session.commit()
        print(f"Movie '{existing.title}' updated successfully!")

    def delete_movie(self, movie_id):
        """This method deletes a movie from the database by its ID."""
        movie = Movie.query.get_or_404(movie_id)
        db.session.delete(movie)
        db.session.commit()
        print(f"Movie with ID {movie_id} deleted successfully!")
