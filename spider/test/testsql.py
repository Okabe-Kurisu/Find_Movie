import traceback

from sqlHelper.db import DBSession, Movie, Filmman, Tag

if __name__ == "__main__":
    session = DBSession()
    try:
        tag = Tag(name="25周1年")
        print(Tag.query_by_name(tag.name, session).id)
    except Exception:
        traceback.print_exc()
        session.rollback()
    session.close()


