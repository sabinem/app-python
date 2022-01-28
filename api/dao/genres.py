from api.data import genres
from api.exceptions.notfound import NotFoundException

class GenreDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """
    def __init__(self, driver):
        self.driver=driver

    """
    This method should return a list of genres from the database with a
    `name` property, `movies` which is the count of the incoming `IN_GENRE`
    relationships and a `poster` property to be used as a background.

    [
       {
        name: 'Action',
        movies: 1545,
        poster: 'https://image.tmdb.org/t/p/w440_and_h660_face/qJ2tW6WMUDux911r6m7haRef0WH.jpg'
       }, ...

    ]
    """
    # tag::all[]
    def all(self):
        # TODO: Open a new session
        # TODO: Define a unit of work to Get a list of Genres
        # TODO: Execute within a Read Transaction

        return genres
    # end::all[]


    """
    This method should find a Genre node by its name and return a set of properties
    along with a `poster` image and `movies` count.

    If the genre is not found, a NotFoundError should be thrown.
    """
    # tag::find[]
    def find(self, name):
        # Define a unit of work to find the genre by it's name
        def find_genre(tx, name):
            first = tx.run("""
                MATCH (g:Genre {name: $name})<-[:IN_GENRE]-(m:Movie)
                WHERE m.imdbRating IS NOT NULL AND m.poster IS NOT NULL AND g.name <> '(no genres listed)'
                WITH g, m
                ORDER BY m.imdbRating DESC

                WITH g, head(collect(m)) AS movie

                RETURN g {
                    .name,
                    movies: size((g)<-[:IN_GENRE]-()),
                    poster: movie.poster
                } AS genre
            """, name=name).single()

            # If no records are found raise a NotFoundException
            if first == None:
                raise NotFoundException()

            return first.get("genre")

        # Open a new session
        with self.driver.session() as session:
            # Execute within a Read Transaction
            return session.read_transaction(find_genre, name)
    # end::find[]