import os
import ast
import uuid
import json 
import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..utils.Logger import setup_logger

class RagDatabase:
    def __init__(self):
        self.logger = setup_logger("rag", stream=False)
        # database settings
        self.collection_name = "news_articles"
        
        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.database_dir = f"{cur_path}/../../database/NewsAgentChroma"
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        self.client = chromadb.PersistentClient(path=self.database_dir, settings=Settings(allow_reset=True))
        
        self.load_database()
    
    def load_database(self):
        # load the database
        try:
            self.db = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "News articles"}
            )
            
            self.logger.info(f"Loaded database from {self.database_dir}")
        except Exception as e:
            self.logger.error(f"Failed to load database: {e}")
            raise e
        
    def similarity_search(self, query, n_results=5):
        try:
            results = self.db.query(
                query_texts=[query],
                n_results=n_results
            )
            self.logger.info(f"Fetched {n_results} results for query: {query}. Results: {results}")
        except Exception as e:
            self.logger.error(f"Failed to fetch results for query: {query}. Error: {e}")
            return None
        
        
        results = [
            {
                "id": doc[0],
                "page_content": doc[1],
                "metadata": doc[2]
            }
            for doc in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])
        ]
        
        return results
    
    
    def article_exist(self, url):
        doc = self.db.get(where={"url": url})
        
        self.logger.info(f"Fetched document with URL: {url}. Document: {doc}")
        # return if the document exist
        if doc and len(doc["documents"]) > 0:
            return True
        else:
            return False
    
    def insert_article(self, document, metadata):
        article_id = str(uuid.uuid4())
        # insert document into the database
        try:
            self.db.add(
                documents=[document],
                metadatas=[metadata],
                ids=[article_id]
            )
            self.logger.info(f"Inserted article with UUID: {article_id}")
        except Exception as e:
            self.logger.error(f"Failed to insert article: {e}")
    
    def get_article_by_id(self, article_id):
        try:
            docs = self.db.get(
                ids=[article_id]
            )
            self.logger.info(f"Fetched article with UUID: {article_id}. Document: {docs}")
        except Exception as e:
            self.logger.error(f"Failed to fetch article with UUID: {article_id}. Error: {e}")
        
        docs = [
            {
                "id": doc[0],
                "page_content": doc[1],
                "metadata": doc[2]
            }
            for doc in zip(docs['ids'], docs['documents'], docs['metadatas'])
        ]
        
        if len(docs) == 1:
            return docs[0]
        else:
            return None
    
    # get articles with missing tags (no tags field or value = [])
    def get_missing_tags(self):
        try:
            docs = self.db.get(
                where={"tags": '[]'}
            )
            self.logger.info(f"Fetched {len(docs['ids'])} articles with missing tags. {docs}")
        except Exception as e:
            self.logger.error(f"Failed to fetch articles with missing tags: {e}")
            docs = None
            
        docs = [
            {
                "id": doc[0],
                "page_content": doc[1],
                "metadata": doc[2]
            }
            for doc in zip(docs['ids'], docs['documents'], docs['metadatas'])
        ]
            
        return result
    
    def update_metadata(self, id, metadata):
        # update metadata of the document
        try:
            self.db.update(
                ids=[id],
                metadatas=[metadata]
            )
            self.logger.info(f"Updated metadata for article with UUID: {id}")
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
    
    def reset_database(self):
        # delete all news from db
        try:
            # drop table
            self.client.drop_collection(self.collection_name)
            self.load_database()
        except Exception as e:
            self.logger.error(f"Failed to reset database: {e}")
            
        self.logger.info(f"Deleted all news.")
    
    def clear_old_news(self):
        # clear news with fetch_date older than 1 week from db
        week_ago = int(datetime.now() - timedelta(days=7)).timestamp()
        result = self.db.delete(where={"fetch_date": {"$lt": week_ago}})
        self.logger.info(f"Deleted {result['n']} news older than 1 week.")
        
    def show_db_summary(self):
        # Number of documents
        num_docs = self.db.count()

        # get folder size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.database_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        total_size = total_size / (1024 * 1024)  # Convert to MB
        
        summary = (
            f"Database Summary:\n"
            f"- Number of Documents: {num_docs}\n"
            f"- Database Size on Disk: {total_size:.2f} MB"
        )
        print(summary)
        return summary
    
    def tags_summary(self):
        # get all tags and do some analysis
        # get all documents
        docs = self.db.get()

        # get all tags
        all_tags = []
        for doc in docs['metadatas']:
            # get the tags from the metadata
            tags = ast.literal_eval(doc['tags'])
            all_tags.extend(tags)
        
        # count the frequency of each tag
        tag_counts = {}
        for tag in all_tags:
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1

        # sort the tags by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        print("======== Tags Summary ========")
        
        print(f"Total number of unique tags: {len(sorted_tags)}")
        self.logger.info(f"Total number of unique tags: {len(sorted_tags)}")
        
        print(f"Total number of tag occurences: {len(all_tags)}")
        self.logger.info(f"Total number of tag occurences: {len(all_tags)}")
        
        print(f"Average frequency of tags: {sum([count for _, count in sorted_tags]) / len(sorted_tags)}")
        self.logger.info(f"Average frequency of tags: {sum([count for _, count in sorted_tags]) / len(sorted_tags)}")
        
        # get the top 10 tags
        top_tags = sorted_tags[:10]

        # print the top 10 tags
        print("Top 10 tags:")
        for tag, count in top_tags:
            print(f"{tag}: {count}")
        

    
if __name__ == '__main__':
    rag_db = RagDatabase()
    rag_db.tags_summary()
    rag_db.show_db_summary()
    
    

'''
{
  "user_id": "user123",
  "name": "John Doe",
  "interests": {
    "AI": 0.3,
    "healthcare": 0.2,
    "gaming": 0.5
  },
  "preferences": {
    "tags": {
      "time_scaling_factor": 0.95,
      "removal_threshold": 0.05,
      "click_score": 0.1,
      "bookmark_score": 0.3
    },
    "ranking": {
      "description": "weights and setting for ranking retrieved articles",
      "interest_weight": 0.2,
      "embeddings_similarity_weight": 0.4,
      "llm_weight": 0.4
    }
  }
}

'''