import os
import ast
import json
import uuid
import sqlite3

from ..utils.Logger import setup_logger

class BookmarkDatabase:
    def __init__(self, rag_database=None):
        self.conn = sqlite3.connect("../../database/NewsAgent.db")
        self.cursor = self.conn.cursor()
        if rag_database:
            self.rag_database = rag_database
        
        self.logger = setup_logger("bookmark")
        
        # create table if not exists bookmarks
        if not self.table_exists("bookmarks"):
            self.create_table()
        
    def create_table(self):
        # id, title, summary, url, tags, fetch_date
        self.cursor.execute("""
                CREATE TABLE bookmarks (
                    bookmark_id TEXT PRIMARY KEY,
                    article_id TEXT,
                    title TEXT,
                    summary TEXT,
                    url TEXT,
                    tags TEXT,
                    fetch_date TEXT,
                    note TEXT,
                    user_id TEXT,
                    workspace_id TEXT
                )
            """)
        self.conn.commit()
        self.logger.info("Created bookmarks table in the database")
        
    def table_exists(self, table_name):
        try:
            result = self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if result.fetchone():
                return True
            else:
                return False
        except Exception as e:
            data_logger.error(f"Failed to check if table exists: {e}")
            return False

    def get_all_bookmarks(self, user_id, workspace_id):
        # get all bookmarks
        self.cursor.execute("SELECT * FROM bookmarks WHERE user_id=? AND workspace_id=?", (user_id, workspace_id))
        rows = self.cursor.fetchall()
        
        self.logger.info(f"Fetched all bookmarks for user {user_id} in workspace {workspace_id}: {rows}")
        
        bookmarks = []
        for row in rows:
            # unify format with news object in other components
            bookmark = {
                "bookmark_id": row[0],
                "article_id": row[1],
                "page_content": row[3],
                "metadata": {
                    "title": row[2],
                    "url": row[4],
                    "tags": ast.literal_eval(row[5]) if row[5] else [],  # convert string to list
                    "fetch_date": row[6]
                },
                "note": row[7] if row[7] else ""
            }
            bookmarks.append(bookmark)
        
        return bookmarks

    def get_all_bookmark_ids(self):
        # get all bookmarks
        self.cursor.execute("SELECT bookmark_id FROM bookmarks")
        rows = self.cursor.fetchall()
        
        self.logger.info(f"Fetched all ids of bookmarks: {rows}")
        
        ids = [row[0] for row in rows]
        
        return ids
    
    def get_all_article_ids(self, user_id, workspace_id):
        # get all article ids
        self.cursor.execute("SELECT article_id FROM bookmarks WHERE user_id=? AND workspace_id=?", (user_id, workspace_id,))
        rows = self.cursor.fetchall()
        
        self.logger.info(f"Fetched all ids of articles in bookmarks for workspace {workspace_id}: {rows}")
        
        ids = [row[0] for row in rows]
        
        return ids
    
    # add bookmark status to articles
    def add_bookmark_status(self, articles, user_id, workspace_id):
        # get all bookmark ids
        bookmarked_article_ids = self.get_all_article_ids(user_id, workspace_id)
        
        self.logger.info(f"Querying article ids {[article['id'] for article in articles]} for user {user_id} in workspace {workspace_id}")
        
        for article in articles:
            if article["id"] in bookmarked_article_ids:
                article["bookmarked"] = True
            else:
                article["bookmarked"] = False
                
        return articles
        

    def add_bookmark(self, article_id, user_id, workspace_id):
        self.logger.info(f"Adding bookmark for article with ID: {article_id} for user {user_id} in workspace {workspace_id}")

        article = self.rag_database.get_article_by_id(article_id)
        
        self.logger.info(f"Article fetched: {article}")
        
        if not article:
            self.logger.error(f"Article with ID {article_id} not found in the database.")
            return False

        # check if the article already exists in the bookmarks
        self.cursor.execute("SELECT * FROM bookmarks WHERE article_id=? AND user_id=? AND workspace_id=?", (article_id, user_id, workspace_id))

        if self.cursor.fetchone():
            self.logger.info(f"Article with ID {article_id} already exists in the bookmarks.")
            return False
        

        # insert the article into the bookmarks table
        if not article["metadata"]["tags"]:
            article["metadata"]["tags"] = []
            
        self.cursor.execute(f"""
            INSERT INTO bookmarks (bookmark_id, article_id, title, summary, url, tags, fetch_date, note, user_id, workspace_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            article_id,
            article["metadata"]["title"],
            article["page_content"],
            article["metadata"]["url"],
            article["metadata"]["tags"],
            article["metadata"]["fetch_date"],
            "",
            user_id,
            workspace_id,
        ))
        
        self.conn.commit()
        self.logger.info(f"Added bookmark for article with ID: {article_id} for user {user_id} in workspace {workspace_id}")
        return True
        

    def delete_bookmark(self, bookmark_id):
        # delete bookmark
        self.cursor.execute("DELETE FROM bookmarks WHERE bookmark_id=?", (bookmark_id,))
        self.conn.commit()
        self.logger.info(f"Deleted bookmark {bookmark_id}")
        return True
    
    def delete_bookmark_by_article(self, article_id, user_id, workspace_id):
        # delete bookmark by article id
        self.cursor.execute("DELETE FROM bookmarks WHERE article_id=? AND user_id=? AND workspace_id=?", (article_id, user_id, workspace_id))
        self.conn.commit()
        self.logger.info(f"Deleted bookmark for article {article_id} for user {user_id} in workspace {workspace_id}")
        return True
    
    def delete_all_bookmarks(self, user_id, workspace_id):
        # delete all bookmarks for a user
        self.cursor.execute("DELETE FROM bookmarks WHERE user_id=? AND workspace_id=?", (user_id, workspace_id))
        self.conn.commit()
        self.logger.info(f"Deleted all bookmarks for user {user_id} in workspace {workspace_id}")
        return True
    
    def reset_database(self):
        # delete table and recreate it
        self.cursor.execute("DROP TABLE IF EXISTS bookmarks")
        self.conn.commit()
        self.create_table()
        self.logger.info("Reset bookmarks database")
        
    def print_all_bookmarks(self):
        # print all bookmarks
        self.cursor.execute("SELECT * FROM bookmarks")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)
    
if __name__ == "__main__":
    # reset database
    bookmark_db = BookmarkDatabase()
    bookmark_db.reset_database()