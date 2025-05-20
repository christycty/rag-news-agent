import os
import uuid
import json
import sqlite3

from ..utils.Logger import setup_logger

class WorkspaceDatabase:
    def __init__(self, rag_database):
        
        self.logger = setup_logger("workspaces")
        self.rag_database = rag_database
        
        # setup database
        self.collection_name = "workspaces"
        
        self.conn = sqlite3.connect("../../database/NewsAgent.db")
        self.cursor = self.conn.cursor()
        
        # create table if not exists bookmarks
        if not self.table_exists(self.collection_name):
            self.create_table()
        
    def create_table(self):
        # id 
        self.cursor.execute("""
                CREATE TABLE workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    user_id TEXT
                )
            """)
        self.conn.commit()
        
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

    def get_all_workspaces(self):
        self.cursor.execute(f"SELECT * FROM {self.collection_name}")
        return self.cursor.fetchall()

    def get_workspaces_by_user_id(self, user_id):
        self.cursor.execute(f"SELECT * FROM {self.collection_name} WHERE user_id=?", (user_id,))
        result = self.cursor.fetchall()

        workspaces = []
        for row in result:
            workspace = {
                "id": row[0],
                "name": row[1],
                "user_id": row[2]
            }
            workspaces.append(workspace)
        
        return workspaces

    def get_workspace_by_id(self, workspace_id):
        self.cursor.execute(f"SELECT * FROM {self.collection_name} WHERE id=?", (workspace_id,))
        return self.cursor.fetchone()

    def add_workspace(self, user_id, workspace_name):
        # check if workspace already exists
        self.cursor.execute(f"SELECT * FROM {self.collection_name} WHERE name=? AND user_id=?", (workspace_name, user_id))
        result = self.cursor.fetchone()
        
        if result:
            raise ValueError(f"Workspace with name {workspace_name} for user {user_id} already exists")
        
        # generate a unique id for the workspace
        workspace_id = str(uuid.uuid4())    
        
        # insert the new workspace into the database
        self.cursor.execute(f"INSERT INTO {self.collection_name} (id, name, user_id) VALUES (?, ?, ?)", (workspace_id, workspace_name, user_id))
        self.conn.commit()
        
        return {
            "id": workspace_id,
            "name": workspace_name,
            "user_id": user_id
        }
        
    def delete_workspace(self, user_id, workspace_id):
        # delete the workspace from the database
        self.logger.info(f"Deleting workspace with id {workspace_id} for user {user_id}")
        self.cursor.execute(f"DELETE FROM {self.collection_name} WHERE id=? AND user_id=?", (workspace_id, user_id))
        self.conn.commit()
        
        return {
            "status": "success",
            "message": f"Workspace with id {workspace_id} deleted"
        }