""" server.py
The main entry point for the FastAPI server.
"""
# server accessed through api
import os
import fastapi, pydantic
import dotenv
from fastapi.middleware.cors import CORSMiddleware

# import custom modules
from .utils.ServerConfig import ServerConfig
from .utils.Logger import setup_logger
from .utils.DataFetcher import DataFetcher

from .databases.Interest import InterestDatabase
from .databases.ArticleRag import RagDatabase
from .databases.Bookmarks import BookmarkDatabase
from .databases.Workspace import WorkspaceDatabase

from .query import Query

############ Initial Setup ############
dotenv.load_dotenv()

CLIENT_IP = os.getenv("CLIENT_IP")

api_logger = setup_logger("api", stream=False)

app = fastapi.FastAPI()

origins = [ CLIENT_IP ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load application specific classes
config = ServerConfig()

rag_db = RagDatabase()
workspace_db = WorkspaceDatabase(rag_db)
interest_db = InterestDatabase(config, rag_db=rag_db)
bookmark_db = BookmarkDatabase(rag_db)

rag_query = Query(config=config, rag_db=rag_db, interest_db=interest_db, bookmark_db=bookmark_db)
data_fetcher = DataFetcher(load_model=False, rag_db=rag_db)


############ Routes ############
# root route
@app.get("/")
async def root():
    return {"message": "Hello World"}


############ Query ############
@app.get("/api/daily_news/{user_id}/{workspace_id}")
async def daily_news(user_id: str, workspace_id: str):
    api_logger.info("Received Daily News Request")
    response = rag_query.daily_recommendation(user_id=user_id, workspace_id=workspace_id)
    api_logger.info(f"Response: {response}")
    return response

class QueryRequest(pydantic.BaseModel):
    query: str
    context: str = None
    quote: str = None
    user_id: str
    workspace_id: str
    news_ids: list[str] = None

@app.post("/api/query")
async def query(request: QueryRequest):
    api_logger.info(f"Received Query: {request}")
    
    response = rag_query.generate_response(request.query, context=request.context, quote=request.quote, user_id=request.user_id, workspace_id=request.workspace_id, recommended_news_ids=request.news_ids)
    
    api_logger.info(f"Response: {response}")
    return response


############ User ############
@app.get("/api/user")
async def get_user_id():
    api_logger.info("Received Get User ID Request")
    user_id = "user123"
    api_logger.info(f"Response: {user_id}")
    return user_id

############ Workspace Update ############
@app.get("/api/workspaces/{user_id}")
async def get_workspaces(user_id: str):
    api_logger.info(f"Received Get Workspaces Request: {user_id}")
    workspaces = workspace_db.get_workspaces_by_user_id(user_id)
    api_logger.info(f"Response: {workspaces}")
    return workspaces


@app.post("/api/workspace/{user_id}/{workspace_name}")
async def create_workspace(user_id: str, workspace_name: str):
    api_logger.info(f"Received Create Workspace Request: {user_id}, {workspace_name}")
    result = workspace_db.add_workspace(user_id, workspace_name)
    api_logger.info(f"Response: {result}")
    return result

@app.delete("/api/workspace/{user_id}/{workspace_name}")
async def delete_workspace(user_id: str, workspace_name: str):
    api_logger.info(f"Received Create Workspace Request: {user_id}, {workspace_name}")
    result = workspace_db.delete_workspace(user_id, workspace_name)
    api_logger.info(f"Response: {result}")
    return result

############ User Interest ############
# user clicks on an article link
@app.post("/api/click_article/{user_id}/{workspace_id}/{article_id}")
async def read_article(user_id: str, workspace_id: str, article_id: str):
    api_logger.info(f"Received Click Article Request: {article_id}")
    interest_db.interact_with_article(article_id, interaction="click", user_id=user_id, workspace_id=workspace_id)

# get top n tags of workspace
@app.get("/api/interests/{user_id}/{workspace_id}")
async def get_interests(user_id: str, workspace_id: str):
    api_logger.info(f"Received Get Interests Request: {workspace_id}")
    interests = interest_db.get_top_tags(user_id=user_id, workspace_id=workspace_id)
    api_logger.info(f"Response: {interests}")
    return interests

# reset workspace interest profile
@app.delete("/api/interests/{workspace_id}")
async def reset_interests(workspace_id: str):
    api_logger.info(f"Received Reset Interests Request: {workspace_id}")
    interest_db.reset_user_profile(workspace_id=workspace_id)
    return {"message": "Interests reset successfully"}


# reset entire database
@app.delete("/api/interests")
async def reset_database():
    api_logger.info("Received Reset Database Request")
    interest_db.clear_database()
    return {"message": "Database reset successfully"}


############ Bookmark ############
# add bookmark
@app.post("/api/bookmark/{user_id}/{workspace_id}/{article_id}")
async def add_bookmark(user_id: str, workspace_id: str, article_id: str):
    api_logger.info(f"Received Add Bookmark Request: {article_id}")
    bookmark = bookmark_db.add_bookmark(article_id, user_id, workspace_id) 
    
    interest_db.interact_with_article(article_id, user_id, workspace_id, "bookmark")
    api_logger.info(f"Response: {bookmark}")
    return bookmark

# get all bookmarks
@app.get("/api/bookmarks/{user_id}/{workspace_id}")
async def get_bookmarks(user_id: str, workspace_id: str):
    api_logger.info("Received Get Bookmark Request")
    bookmarks = bookmark_db.get_all_bookmarks(user_id, workspace_id)
    api_logger.info(f"Response: {bookmarks}")
    return bookmarks


# delete bookmark
@app.delete("/api/bookmark/{bookmark_id}")
async def delete_bookmark(bookmark_id: str):
    api_logger.info(f"Received Delete Bookmark Request: {bookmark_id}")
    result = bookmark_db.delete_bookmark(bookmark_id)
    return result

# delete bookmark by workspace and article id
@app.delete("/api/bookmark/{user_id}/{workspace_id}/{article_id}")
async def delete_bookmark_by_article(user_id: str, workspace_id: str, article_id: str):
    api_logger.info(f"Received Delete Bookmark by Article Request: {article_id}")
    bookmark = bookmark_db.delete_bookmark_by_article(article_id, user_id, workspace_id)
    api_logger.info(f"Response: {bookmark}")
    return bookmark

@app.delete("/api/bookmark/all/{user_id}/{workspace_id}")
async def delete_all_bookmarks(user_id: str, workspace_id: str):
    api_logger.info(f"Received Delete All Bookmark Request: {user_id}, {workspace_id}")
    bookmark = bookmark_db.delete_all_bookmarks(user_id, workspace_id)
    api_logger.info(f"Response: {bookmark}")
    return bookmark

########### Server Configuration ###########
@app.get("/api/config")
async def get_config():
    print("Received Get Config Request")
    api_logger.info("Received Get Config Request")
    config_data = config.get_config()
    api_logger.info(f"Response: {config_data}")
    return config_data

############ News Database Management ############
# fetch data from newsapi to update the database
@app.post("/api/database/update")
async def fetch_data(fetchType: str, hours_count: int = None):
    if fetchType == "headline":
        data_fetcher.fetch_data(fetch_type="headline")
    elif fetchType == "everything":
        data_fetcher.fetch_data(fetch_type="everything", hours_count=hours_count)
    
    return {"message": "Data fetched successfully"}

# get database summary
@app.get("/api/database/summary")
async def get_database_summary():
    # create a data fetcher object
    return rag_db.show_db_summary()

# clear database
@app.post("/api/database/reset")
async def reset_database():
    # create a data fetcher object
    return rag_db.reset_database()



