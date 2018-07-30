import traceback

from sql.dbHelper import DBSession, Movie, Filmman

if __name__ == "__main__":
    session = DBSession()
    try:
        movie = Movie.query_by_douban_id("1", session)
        filmmaker = Filmman.query_by_douban_id("1", session)
        filmmaker.save(session)
        movie.append_filmman(filmmaker, Filmman.Role_Writer, session)
    except Exception:
        traceback.print_exc()
        session.rollback()
    session.close()


