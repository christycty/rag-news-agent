import os
import time
import argparse
import requests
from nltk.stem import WordNetLemmatizer
from dotenv import load_dotenv
from datetime import datetime, timedelta
from newsplease import NewsPlease

from ..databases.ArticleRag import RagDatabase
from .Logger import setup_logger 


# initial setup
load_dotenv()
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
class DataFetcher:
    def __init__(self, rag_db=None, load_model=False, model="ust"):        
        self.logger = setup_logger("dataFetcher", "dataFetcher")
        
        self.logger.info(f"Starting DataFetcher with model {model}, rag_db {rag_db} and load_model {load_model}.")
        
        # load RAG database
        if rag_db:
            self.db = rag_db
        else:
            self.db = RagDatabase()
        
        # load LLM for generating tags and summary
        if load_model:
            if model == "ust":
                from ..models.USTModelClient import USTModelClient
                self.model = USTModelClient()
            elif model == "hf":
                from ..models.HuggingFaceModelClient import  HuggingFaceModelClient
                self.model = HuggingFaceModelClient()
            elif model == "ollama":
                from ..models.OllamaModelClient import OllamaModelClient
                self.model = OllamaModelClient() 
            else:
                self.logger.error(f"Model {model} not supported. Please choose from ust, hf, ollama.")
                self.model = None
        else:
            self.model = None
        
        # word lemmatizer for tags processing
        self.lemmatizer = WordNetLemmatizer()
        

    '''
    News Fetching functions
    '''
    # fetch news article from newsapi
    def request_data(self, url):
        # Send a GET request to the API
        response = requests.get(url)

        # check response
        if response.status_code != 200:
            self.logger.error(f"Error fetching data: {response.status_code}")
            return None

        # Parse the response JSON data
        data = response.json()
        total_results = data.get("totalResults", 0)
        self.logger.info(f"fetched {total_results} articles, actually received {len(data.get('articles', []))}")

        # Return the parsed data
        return data, total_results

    # handles full processing of articles
    def fetch_and_store_articles(self, data):
        # Convert articles to text format
        fetch_date = int(datetime.now().timestamp())
        
        self.logger.info(f"Starting to insert {len(data['articles'])} articles into database.")

        for article in data['articles']:
            # check if article is in db
            if  self.db.article_exist(article['url']):
                self.logger.info(f"Article already in database: {article['title']} [url= {article['url']}")
                continue
            
            start_time = time.time()
            # store summary of article instead of full article
            try:
                full_article = NewsPlease.from_url(article['url'])
                self.logger.info(f"Fetched full article: {article['title']} [url= {article['url']}")
                
                # skip if article maintext is empty / None or larger than 4000 tokens
                if not full_article.maintext or len(full_article.maintext) > 4000:
                    self.logger.info(f"Article maintext is empty or too large: {article['title']} [url= {article['url']}")
                    text = article.get("description", "Unknown")
                    tags = []
                    continue
                
                text, tags = self.generate_summary(title=article['title'], content=full_article.maintext)

            except Exception as e:
                self.logger.error(f"Error crawling full article: {str(e)}")
                text = article.get("description", "Unknown")
                tags = []
                continue
                

            metadata = {
                "title": article['title'],
                "description": article.get("description", "Unknown"),
                "url": article['url'],
                "fetch_date": fetch_date,
                "publish_date": article.get("publishedAt", "Unknown"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "tags": str(tags),
            }
            
            try:
                self.db.insert_article(document=text, metadata=metadata)
                
                self.logger.info(f"Added article into database using {time.time() - start_time} seconds: {article['title']}")
            except Exception as e:
                self.logger.error(f"Error storing article: {str(e)}")
                
                continue
    
    # Entry point for fetching data
    def fetch_data(self, fetch_type="everything", hours_count=12, start_page=1):
        self.logger.info(f"Fetching {fetch_type} data for the last {hours_count} hours.")
        # Get the API key from environment variables
        API_KEY = os.getenv("NEWS_API_KEY")
        
        if (fetch_type == "headline"):
            base_url = f"https://newsapi.org/v2/top-headlines?category=technology&apiKey={API_KEY}&pageSize=100"
       
        else:
            # API has 24 hour delay, so have to fetch at least one day ahead 
            # since we are fetching from us, cater the timezone difference too
            end_datetime = datetime.now() - timedelta(days=1) - timedelta(hours=12)
            start_datetime = (end_datetime - timedelta(hours=hours_count))
            
            # Convert the datetime objects to ISO format strings
            end_datetime = end_datetime.isoformat()
            start_datetime = start_datetime.isoformat()
            
            base_url = f"https://newsapi.org/v2/everything?q=technology&language=en&from={start_datetime}&to={end_datetime}&apiKey={API_KEY}&pageSize=100"

        # Fetch data from newsapi
        try:
            data, total_results = self.request_data(base_url)
            self.logger.info(f"Fetched {total_results} articles from newsapi.")
        except Exception as e:
            self.logger.error(f"Error fetching data from newsapi: {str(e)}")
            return
        
        if total_results == 0:
            self.logger.error("No articles found.")
            return
        
        page_count = (total_results - 1) // 100 + 1
        # temp: try 3 pages first
        # page_count = min(page_count, 3)
        for page in range(start_page, page_count + 1):
            try:
                data, _ = self.request_data(base_url + f"&page={page}")
                self.logger.info(f"Fetched {len(data['articles'])} articles from page {page}.")
            except Exception as e:
                self.logger.error(f"Error fetching data from newsapi: {str(e)}")
                return
            self.fetch_and_store_articles(data)
    
    
    '''
    Use LLM to generate summary and tags for articles
    '''
    # generate summary and tags from raw article
    def generate_summary(self, title, content):
        prompt = (
            f"Generate a 150-word summary and 5 category tags for the following news article. "
            f"Focus on the key points from the title and content, keeping it concise and informative.\n\n"
            f"Title: {title}\n"
            f"Content: {content}\n\n"
            f"Return the summary enclosed by the tags <summary></summary>\n"
            f"Return the category tags enclosed by <tags></tags> and separated by comma. Example: <tags>AI,healthcare,gaming,Nintendo,Xbox</tags>\n"
        )
        
        response = self.model.get_model_response(prompt)
        response = response.replace("Tags", "tags")
        
        self.logger.info(f"Response from model: {response}")
        
        
        if "<summary>" in response and "</summary>" in response:
            summary = response.split("<summary>")[1].split("</summary>")[0]
        else:
            summary = response
        
        if "<tags>" in response and "</tags>" in response:
            tags = response.split("<tags>")[1].split("</tags>")[0]
            tags = tags.split(",")
        else:
            tags = []
            
        # postprocess each tag: (1) trim space, (2) convert to lower case, (3) lemmatization
        tags = [self.lemmatizer.lemmatize(tag.strip().lower()) for tag in tags]
            
        self.logger.info(f"Generated tags {tags} and summary for {title}:\n{summary}")
        return summary, tags

    # generate tags from news summary
    def generate_tags_from_summary(self, summary):
        # Generate tags from the summary using the model
        prompt = (
            f"Generate 5 category tags for the following summary. "
            f"Focus on the key points, keeping it concise and informative.\n\n"
            f"Summary: {summary}\n\n"
            f"Return the category tags enclosed by <tags></tags> and separated by comma. Example: <tags>AI,healthcare,gaming,Nintendo,Xbox</tags>\n"
        )
        
        response = self.model.get_model_response(prompt)
        response = response.replace("Tags", "tags")
        
        self.logger.info(f"Response from model: {response}")
        
        if "<tags>" in response and "</tags>" in response:
            tags = response.split("<tags>")[1].split("</tags>")[0]
            tags = tags.split(",")
        else:
            tags = []
            
        # postprocess each tag: (1) trim space, (2) convert to lower case, (3) lemmatization
        tags = [self.lemmatizer.lemmatize(tag.strip().lower()) for tag in tags]
        
        self.logger.info(f"Generated tags {tags} from summary:\n{summary}")
        return tags
    
    '''
    Database cleaning
    ''' 
    # generate tags for articles without tags in db  
    def fill_missing_tags(self):
        
        result = self.db.get_missing_tags()
        
        if not result:
            self.logger.info("No documents with missing 'tags' field found.")
            return
        
        result = [
            {
                "id": doc[0],
                "document": doc[1],
                "metadata": doc[2]
            }
            for doc in zip(result['ids'], result['documents'], result['metadatas'])
        ]
        
        self.logger.info(f"Found {len(result)} documents with missing 'tags' field.")
        
        
        for i, entry in enumerate(result):
            
            self.logger.info(f"Processing document {i + 1}, entry metadata: {entry['metadata']}")
            
            metadata = entry['metadata']
            summary = entry['document']
            
            # generate tags
            tags = self.generate_tags_from_summary(summary)
            
            metadata['tags'] = str(tags)
            
            self.db.update_metadata(id=entry['id'], metadata=metadata)
            
            self.logger.info(f"Updated tags for article: {metadata['title']} , tags= {tags}")

    def clear_old_news(self):
        # clear old news from db
        self.db.clear_old_news()
    
    
if __name__ == "__main__":
    # argparse if --reset_db is passed, dump database
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset_db", "-r", action="store_true", help="Reset database")
    parser.add_argument("--fetch_everything", "-e", action="store_true", help="Fetch everything")
    parser.add_argument("--fetch_headline", "-hl", action="store_true", help="Fetch headline")
    parser.add_argument("--hours_count", "-hr", type=int, help="Number of hours to fetch data from", default=12)
    parser.add_argument("--clean", "-c", action="store_true", help="Clean database")
    parser.add_argument("--export", "-ex", action="store_true", help="Export database to json")
    parser.add_argument("--model", "-m", type=str, help="Model name: ust, hf or ollama", default="none")
    parser.add_argument("--start_page", "-sp", type=int, help="Start page for fetching data", default=1)
    
    args = parser.parse_args()
    
    rag_db = RagDatabase()
    
    # check if gpu available
    if not args.model or args.model == "none":
        data_fetcher = DataFetcher(load_model=False, rag_db=rag_db)
    else:
        data_fetcher = DataFetcher(load_model=True, model=args.model, rag_db=rag_db)
    
    if args.reset_db:
        data_fetcher.db.reset_database()
        
    if args.fetch_everything:
        data_fetcher.fetch_data(fetch_type="everything", hours_count=args.hours_count, start_page=args.start_page)
    

    if args.fetch_headline:
        data_fetcher.fetch_data(fetch_type="headline")
    
    if args.clean:
        data_fetcher.clear_old_news()
        # data_fetcher.fill_missing_tags()
        
    data_fetcher.db.show_db_summary()
    
    
