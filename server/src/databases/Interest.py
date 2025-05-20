"""
    UserProfile class to manage tag-based user profiles.
"""
import os
import ast
import uuid
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..utils.Logger import setup_logger


class InterestDatabase:
    def __init__(self, config=None, rag_db=None):
        self.config = config
        self.rag_db = rag_db
        
        self.logger = setup_logger("interest", stream=False)
        
        # load database
        self.collection_name = "user_interests"
        
        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.database_dir = f"{cur_path}/../../database/NewsAgentChroma"
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        self.client = chromadb.PersistentClient(path=self.database_dir, settings=Settings(allow_reset=True))
        
        self.db = self.client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=self.embedding_function
        )
        
    def add_score(self, tag, score, user_id, workspace_id):
        # check if tag exists in the database
            result = self.db.get(
                where={"$and": [ {"tag": tag}, {"workspace_id": workspace_id}]}
            )
            
            self.logger.info(f"Retrieved result {result} for tag {tag}")
            
            # insert new tag
            if len(result["documents"]) == 0:
                metadata = {
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "tag": tag,
                    "score": score
                }
                self.db.add(
                    documents=[tag],
                    metadatas=[metadata],
                    ids=[str(uuid.uuid4())]
                )
                self.logger.info(f"Inserted new tag {tag} with metadata {metadata}")
                
            # get score and add score based on config
            else:
                metadata = result["metadatas"][0]
                
                metadata["score"] += score
                
                self.db.update(
                    ids=[result["ids"][0]],
                    metadatas=[metadata]
                ) 
                
                self.logger.info(f"Updated tag {tag} with metadata {metadata}")
                
    
    def interact_with_article(self, article_id,  user_id, workspace_id, interaction="click",):
        if interaction not in ["click", "bookmark"]:
            raise ValueError(f"Invalid interaction: {interaction}")
        
        article = self.rag_db.get_article_by_id(article_id)
        
        # if article does not exist or contains no tags, return
        if article is None or article["metadata"]["tags"] is None:
            self.logger.info(f"Article {article_id} has no tags")
            return
        
        tags = ast.literal_eval(article["metadata"]["tags"])
        self.logger.info(f"Clicked tags: {tags}")
        
        # update each tag
        base_score = self.config.tags[f"{interaction}_score"]
        for tag in tags:
            self.add_score(
                tag,
                base_score,
                user_id,
                workspace_id
            )
            
            # TODO: this is extremely slow, we need to optimize this
            '''similar_tags = self.get_similar_tags(tag)
            
            for similar_tag in similar_tags["documents"][0]:
                self.add_score(
                    similar_tag,
                    base_score * self.config.tags["similar_tag_weight"],
                    user_id,
                    workspace_id
                )
                '''
    
    # add some score to similar tags
    def get_similar_tags(self, tag, result_count=5):
        # retrieve 20 similar tags
        # here we are only caring the sementic similarity of the tags, the associated users or workspace are not important
        similar_tags = self.db.query(
            query_texts=[tag],
            n_results=20
        )
        
        self.logger.info(f"Similar tags for {tag}: {similar_tags}")
        
        return similar_tags
    
    def get_tag_score(self, tag):
        result = self.db.get(
            where={"tag": tag}
        )
        # get tag score
        if len(result["documents"]) == 0:
            # self.logger.info(f"Tag {tag} not found")
            return 0
        else:
            tag_score = result["metadatas"][0]["score"]
            self.logger.info(f"Tag {tag} score: {tag_score}")
            return tag_score
    
    def get_top_tags(self, user_id, workspace_id, tag_count=10):
        # get top tags from the user profile
        self.logger.info(f"Fetching top tags for workspace {workspace_id}")

        # get all tags
        if workspace_id:
            result = self.db.get(
                where={"workspace_id": workspace_id}
            )
        else:
            result = self.db.get()
            
        all_tags = []
        for doc in result["metadatas"]:
            all_tags.append( (doc["tag"], doc["score"]) )
        # sort tags by score
        all_tags.sort(key=lambda x: x[1], reverse=True)
        
        # get top tags
        top_tags = [tag[0] for tag in all_tags[:tag_count]]
        
        self.logger.info(f"Fetched top tags: {top_tags}")
        return top_tags
    
    def reset_workspace_profile(self, workspace_id):
        self.db.delete(
            where={"workspace_id": workspace_id}
        )
    
    
    def clean_database(self):
        result = self.db.get()
        metadatas = result["metadatas"]
        
        # change all profile_id to workspace_id
        for metadata in metadatas:
            metadata["workspace_id"] = SPACE_ID
            del metadata["profile_id"]
            
        self.db.update(
            ids=result["ids"],
            metadatas=metadatas
        )
        self.logger.info("Database updated")
    
    # clear entire database
    def clear_database(self):
        self.client.delete_collection(self.collection_name)
        
        self.db = self.client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=self.embedding_function
        )
        
        self.logger.info("Database cleared")
            
if __name__ == "__main__":
    interest_db = InterestDatabase()
    # interest_db.clean_database()