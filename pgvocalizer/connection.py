import os

from dotenv import load_dotenv
import psycopg2

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


def _create_connection_cursor():
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" %
                            (os.environ.get("PG_DBNAME"), os.environ.get("PG_USER"),
                             os.environ.get("PG_HOST"), os.environ.get("PG_PASSWORD")))

    return conn.cursor()


def get_query_plan(query):
    cur = _create_connection_cursor()
    query_explain = "EXPLAIN (FORMAT JSON) " + query

    cur.execute(query_explain)
    res = cur.fetchone()[0][0]

    cur.close()

    return res
