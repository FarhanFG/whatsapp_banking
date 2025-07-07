from fastapi import FastAPI, Query
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load DB config from environment variables
DB_CONFIG = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
}

@app.get("/api/rbi")
def get_rbi_data(type: str = Query(..., regex="^(press-release|publication)$")):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if type == "press-release":
           query = """
        SELECT id, title, link, published_date, summary, status, fetched_at
        FROM cr_rbi_press_releases
        ORDER BY fetched_at DESC, id DESC;
            """
        elif type == "publication":
            query = """
        SELECT id, title, link, summary, published_date, fetched_at
        FROM cr_rbi_publications
        ORDER BY fetched_at DESC, id DESC;
            """


        cursor.execute(query)
        results = cursor.fetchall()
        

        return {"data": results}
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
