import psycopg2
import os

# Paste your Neon Database URL here
DATABASE_URL = "postgresql://user:password@ep-rest-of-host.region.aws.neon.tech/dbname?sslmode=require"

movies_data = [
    (0, "Inception", "Sci-Fi", 8.8),
    (1, "Interstellar", "Sci-Fi", 8.6),
    (2, "The Dark Knight", "Action", 9.0),
    (3, "The Matrix", "Sci-Fi", 8.7),
    (4, "Avengers: Endgame", "Action", 8.4),
    (5, "The Shawshank Redemption", "Drama", 9.3),
    (6, "Forrest Gump", "Drama", 8.8),
    (7, "Parasite", "Thriller", 8.5),
    (8, "Joker", "Thriller", 8.4),
    (9, "Get Out", "Horror", 7.7),
    (10, "A Quiet Place", "Horror", 7.5),
    (11, "Toy Story", "Animation", 8.3),
    (12, "Spirited Away", "Animation", 8.6),
    (13, "The Grand Budapest Hotel", "Comedy", 8.1)
]

def seed_database():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INT PRIMARY KEY,
            title VARCHAR(255),
            genre VARCHAR(100),
            rating FLOAT
        );
    """)
    cursor.execute("TRUNCATE TABLE movies;")
    
    insert_query = "INSERT INTO movies (id, title, genre, rating) VALUES (%s, %s, %s, %s)"
    cursor.executemany(insert_query, movies_data)
    
    conn.commit()
    print("Neon Database seeded successfully!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_database()