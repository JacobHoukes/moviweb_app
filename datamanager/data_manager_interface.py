from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    @abstractmethod
    def get_all_users(self):
        """This method retrieves all users from the database."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """This method retrieves all movies for a given user by user ID."""
        pass

    @abstractmethod
    def add_user(self, user):
        """This method adds a new user to the database."""
        pass

    @abstractmethod
    def add_movie(self, movie):
        """This method adds a new movie to the database."""
        pass

    @abstractmethod
    def update_movie(self, movie):
        """This method updates an existing movie's information in the database."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """This method deletes a movie from the database using its ID."""
        pass
