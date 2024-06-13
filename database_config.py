import psycopg2
from psycopg2 import sql
import subprocess

# Ensure PostgreSQL service is running
def start_postgresql_service():
    try:
        subprocess.run(['sudo', 'service', 'postgresql', 'start'], check=True)
        print("PostgreSQL service started successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error starting PostgreSQL service: {e}")

def create_connection(dbname, user, password, host='localhost', port='5432'):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print("Connection successful")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_database(conn, new_dbname):
    try:
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_dbname)))
        print(f"Database '{new_dbname}' created successfully")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        conn.autocommit = False

def create_table(conn, table_name, table_schema):
    try:
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} ( {} )").format(
            sql.Identifier(table_name),
            sql.SQL(table_schema)
        ))
        conn.commit()
        print(f"Table '{table_name}' created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()
    finally:
        cursor.close()

if __name__ == "__main__":
    # Start PostgreSQL service
    start_postgresql_service()

    default_db_conn = create_connection('postgres', 'guviuser', 'password')

    if default_db_conn:
        new_dbname = 'youtube_data_harvesting'
        create_database(default_db_conn, new_dbname)
        default_db_conn.close()

        # Connection to the newly created database to create tables
        new_db_conn = create_connection(new_dbname, 'guviuser', 'password')

        if new_db_conn:
            # Schema for the 'channel' table
            channel_table_schema = """
            channel_id VARCHAR(255) PRIMARY KEY,
            channel_name VARCHAR(255),
            channel_type VARCHAR(255),
            channel_views INT,
            channel_description TEXT,
            channel_status VARCHAR(255)
            """
            create_table(new_db_conn, 'youtube_channel', channel_table_schema)

            # Schema for the 'playlist' table
            playlist_table_schema = """
            playlist_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255),
            playlist_name VARCHAR(255),
            FOREIGN KEY (channel_id) REFERENCES channel(channel_id)
            """
            create_table(new_db_conn, 'youtube_playlist', playlist_table_schema)

            # Schema for the 'comment' table
            comment_table_schema = """
            comment_id VARCHAR(255) PRIMARY KEY,
            video_id VARCHAR(255),
            comment_text TEXT,
            comment_author VARCHAR(255),
            comment_published_date TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES video(video_id)
            """
            create_table(new_db_conn, 'youtube_comment', comment_table_schema)

            # Schema for the 'video' table
            video_table_schema = """
            video_id VARCHAR(255) PRIMARY KEY,
            playlist_id VARCHAR(255),
            video_name VARCHAR(255),
            video_description TEXT,
            published_date TIMESTAMP,
            view_count INT,
            like_count INT,
            dislike_count INT,
            favorite_count INT,
            comment_count INT,
            duration INT,
            thumbnail VARCHAR(255),
            caption_status VARCHAR(255),
            FOREIGN KEY (playlist_id) REFERENCES playlist(playlist_id)
            """
            create_table(new_db_conn, 'youtube_video', video_table_schema)

            new_db_conn.close()
