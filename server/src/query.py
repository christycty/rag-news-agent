import os
import re
import ast
import json
import uuid
import time 
import requests
from dotenv import load_dotenv
from newsplease import NewsPlease

from .databases.ArticleRag import RagDatabase
from .databases.Bookmarks import BookmarkDatabase
from .databases.Interest import InterestDatabase
from .models.USTModelClient import USTModelClient

from .utils.Logger import setup_logger 
from .utils.ServerConfig import ServerConfig

load_dotenv()

class Query:
    def __init__(self, config=None, rag_db=None, interest_db=None, bookmark_db=None):
        self.config = config
        
        self.logger = setup_logger("query")
        self.model = USTModelClient()
        
        if rag_db:
            self.db = rag_db
        else:
            self.db = RagDatabase()
        
        if interest_db:
            self.interest_db = interest_db
        else:
            self.interest_db = InterestDatabase()
        
        if bookmark_db:
            self.bookmark_db = bookmark_db
        else:
            self.bookmark_db = BookmarkDatabase(self.db)
    
    
    def retrieve_data(self, query, result_count=10):
        # Retrieve documents from vector database
        self.logger.info(f"Retrieving documents for query: {query}")
        docs = self.db.similarity_search(query, n_results=result_count)
        self.logger.info(f"Retrieved {len(docs)} documents")
        return docs
    
    def generate_article_prompt(self, articles):
        result = ""
        for i, article in enumerate(articles):
            result += (
                f"index={i}:\n"
                f"title={article['metadata']['title']}\n"
                f"description/summary={article['page_content']}\n"
            )
        return result
    
    # combine user query and user profile to generate keywords for RAG
    def generate_keywords(self, user_input):
        """
        Generate keywords for RAG retrieval using the LLM.
        :param user_input: String, e.g., "latest AI news"
        :param user_profile: Dict, e.g., {"interests": ["AI", "startups"]}
        :return: List of keywords
        """
        prompt = (
            f"You are an AI assistant tasked with generating keywords for a news retrieval system. "
            f"The user has provided the following input: '{user_input}'. "
            f"Based on this input, generate a list of 1 to 5 relevant keywords that best represent the topics to search for."
            f"Focus on specific, concise terms that is closely related to user's query, avoid overly broad or irrelevant words. "
            f"Avoid keywords with similar meanings or synonyms. "
            f"Return the keywords as a comma-separated list wrapped in <keywords> tags, formatted exactly as '<keywords>keyword1, ...</keywords>'. "
            f"For example, if the input is 'give me some cool AI startups', you might return '<keywords>AI, startups</keywords>'. "
            f"Do not include explanations, extra text, or deviations from this format:\n\n"
        )
        try:
            response = self.model.get_model_response(prompt)
            match = re.search(r"<keywords>(.*?)</keywords>", response)
            if match:
                keywords = [kw.strip() for kw in match.group(1).split(",")]
                self.logger.info(f"Generated keywords: {keywords}")
                return keywords
            else:
                self.logger.warning(f"Invalid keyword format from LLM: {response}")
                return user_input.split()  # Fallback
        except Exception as e:
            self.logger.error(f"Error generating keywords: {str(e)}")
            return user_input.split()
    
    def parse_postprocessed_query(self, response):
        # parse the response using string matching
        response = re.match(r"<response>(.*?)</response>", response).group(1)
        
        
        web_search_required = re.search(r"web_search_required=(true|false)", response).group(1)
        
        if web_search_required:
            web_search_phrase = re.search(r"web_search_phrase='(.*?)'", response).group(1)
        
        rag_query = re.search(r"rag_query='(.*?)'", response).group(1)
        
        self.logger.info(f"Parsed response: web_search_required={web_search_required}, web_search_phrase={web_search_phrase}, rag_query={rag_query}")
        
        result = {
            "web_search_required": web_search_required == "true",
            "web_search_phrase": web_search_phrase if web_search_phrase else "",
            "rag_query": rag_query if rag_query else ""
        }
        return result
        
    
    # use LLM to rephrase user query to get better RAG results
    def postprocess_query(self, user_input, user_id, workspace_id, context=None, quote=None):
        # context to specify the task and output format
        agent_context = (
            f"You are a news recommendation expert. Your task is to assist in finding relevant news articles for a user. You will be provided with the user's query, a snippet from a previously recommended article the user is referring to (if applicable), the current conversation history (if applicable) and the top 5 tags the user is interested in (if applicable). "
            f"Based on this information, you must:"
            f"1a.  **Determine if a web search for older news is necessary.** Consider whether the user's query requires historical context or information that might not be included in news within a week."
            f"1b. **Formulate short search phrase for the web search.** This should be a short phrase that can be used to search for older news articles to answer user's query. It should be kept as short as possible, within 1-3 words. "
            f"2.  **Formulate a search query for the RAG database.** This query should be specific and effective in retrieving relevant articles from the database."
            f"Your output should be structured as follows:"
            f"<response>web_search_required=true/false,"
            f"web_search_phrase='search phrase for news', "
            f"rag_query='search query for RAG database'</response>"
        )
        
        # construct prompt
        prompt = (
            f"user_query='{user_input}'. "
            f"previous_article_snippet='{quote if quote else 'none'}'. "
        )
        
        if workspace_id:
            top_tags = self.interest_db.get_top_tags(user_id=user_id, workspace_id=workspace_id, tag_count=5)
            
            prompt += f"top_tags={top_tags}."
            
        if context:
            prompt += f"conversation_history={context}. "
            
        try:
            response = self.model.get_model_response(prompt, context=agent_context)
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
        
        # parse result
        result = self.parse_postprocessed_query(response)
        self.logger.info(f"Postprocessed query: {result}")
        return result
    
    # use web search to get articles
    def web_search(self, phrase):
        web_search_count = self.config.query["web_search_count"]
        # url encode
        search_string = requests.utils.quote(phrase)
        self.logger.info(f"conducting web search using string: {search_string}")
        
        # use thenewsapi for longer time frmae (limited to 3 articles in result)
        url = f"https://api.thenewsapi.com/v1/news/all?search={search_string}&language=en&sort=relevance_score&categories=tech&limit={web_search_count}&api_token={os.getenv("THE_NEWS_API_KEY")}"
        response = requests.get(url)

        # check response
        if response.status_code != 200:
            fetcher_logger.error(f"Error fetching data: {response.status_code}")
            return None

        # Parse the response JSON data
        data = response.json()["data"]
        self.logger.info(f"Fetched {len(data)} articles from web search")
        
        
        result = []
        result_count = min(web_search_count, len(data))
        for i in range(result_count):
            raw_article = data[i]
            parsed_article = {                
                # generate id as hash of url for avoiding repeated articles
                "id": str(uuid.uuid3(uuid.NAMESPACE_DNS, raw_article["url"])),
                "metadata": {
                    "title": raw_article["title"],
                    "description": raw_article["description"],
                    "url": raw_article["url"],	
                },
                "page_content": raw_article["description"]
            }
            result.append(parsed_article)
        
        self.logger.info(f"Web search fetched articles: {[news['metadata']['title'] for news in result]}")
        return result
           
    def select_articles(self, docs, query, web_search_docs=None, recommended_news_ids=None):
        result_count = self.config.query["result_count"]
        candidate_count = self.config.query["candidate_count"]
        rank_mode = self.config.query["article_rank_mode"]
        
        self.logger.info(f"Selecting {result_count} articles under rank mode {rank_mode} for query: {query}")
        selected_indices = []
        
        # combine web search and database result
        if web_search_docs:
            docs = docs[: candidate_count - len(web_search_docs)]
            docs = web_search_docs + docs
            
        scores = [0] * len(docs)
        
        ############ get llm score ############
        article_string = self.generate_article_prompt(docs)
        agent_context = (
            f"You are a news recommendation expert. Your task is to assist in finding relevant news articles for a user. You will be provided with the user's query and a list of candidate articles to choose from."
            f"Based on this information, you must rank all {len(docs)} articles from most to least relevant to the user's query. "                
            f"Your output should be structured as follows:"
            f"<response>[index1, index2, ...]</response>"
            f"All indices should be included in decreasing order of relevance. "
        )
            
        prompt = (
            f"user_query={query}"
            f"articles:\n{article_string}"
        )
        
        start_time = time.time()
        response = self.model.get_model_response(prompt, context=agent_context)
        
        self.logger.info(f"Took {time.time() - start_time} seconds to generate response: {response}")
        
        match = re.search(r"<response>\[(.*?)\]</response>", response)
        if match:
            llm_ranking = [int(i.strip()) for i in match.group(1).split(",")]
        else:
            llm_ranking = []
            
        # use 1-based ranking
        llm_ranking = [(index, rank + 1) for rank, index in enumerate(llm_ranking)]
        self.logger.info(f"LLM ranking: {llm_ranking}")
        
        # get the scores from rankings
        llm_scores = []
        for i, (index, rank) in enumerate(llm_ranking):
            score = 1.0 / rank
            llm_scores.append((index, score))
            
        # normalize llm scores
        total_score = sum([score for _, score in llm_scores])

        if total_score > 0:            
            llm_scores = [(i, score / total_score) for i, score in llm_scores]
            
        # self.logger.info(f"Extract LLM scores {llm_scores}")
        
        for i, score in llm_scores:
            scores[i] += score * self.config.query["llm_weight"]
        
        ############ get tags score ############
        # TODO: consider if tags are really useful here
        tags_scores = []
        for i, doc in enumerate(docs):
            tags = ast.literal_eval(doc["metadata"].get("tags", "[]"))
            score = 0
            for tag in tags:
                score += self.interest_db.get_tag_score(tag)
            
            tags_scores.append((i, score))
            
        # normalize tag scores
        total_score = sum([score for _, score in tags_scores])
        if total_score > 0:
            tags_scores = [(i, score / total_score) for i, score in tags_scores]
        
        # self.logger.info(f"Extract tags scores: {tags_scores}")
        
        # update scores
        for i, score in tags_scores:
            scores[i] += self.config.query["interest_weight"]
        # TODO (optional): get RAG score by embeddings similarity
        
        ############ extract score ############
        scores = [(i, score) for i, score in enumerate(scores)]
        scores.sort(key=lambda x: x[1], reverse=True)
    
        self.logger.info(f"Extract scores: {scores}")
        
        
        # skip recommended articles in this session
        if recommended_news_ids:
            self.logger.info(f"Recommended news ids: {recommended_news_ids}")
            valid_indices = []
            for i, doc in enumerate(docs):
                self.logger.info(f"Document {i}: {doc['metadata']['title']}, id: {doc['id']}")
                if doc["id"] not in recommended_news_ids:
                    valid_indices.append(i)
                    
            for i, score in scores:
                if i not in valid_indices:
                    scores.remove((i, score))
            
            if len(scores) >= result_count:
                selected_indices = [i for i, _ in scores[:result_count]]
                
            # if number of selected articles are less than result_count, greedily select the rest from recommended
            else:
                selected_indices = [i for i, _ in scores]
                for i, doc in enumerate(docs):
                    if doc["id"] in recommended_news_ids:
                        selected_indices.append(i)
                        if len(selected_indices) >= result_count:
                            break
        else:
            selected_indices = [i for i, _ in scores[:result_count]]
            
        selected_indices = selected_indices[:result_count]
        
        self.logger.info(f"Selected indices: {selected_indices}")
        
        selected_articles = [docs[i] for i in selected_indices]
        return selected_articles
    
    def generate_response(self, query,user_id, workspace_id, context=None, quote=None, recommended_news_ids=None):
        # load configs
        rag_mode = self.config.query["rag_mode"]        
        retrieve_count = self.config.query["retrieve_count"]
        
        # ingest query to generate web and rag search strings
        parse_result = self.postprocess_query(query, context=context, user_id=user_id, workspace_id=workspace_id, quote=quote)
        
        # retrieve articles
        docs = self.retrieve_data(parse_result["rag_query"], result_count=retrieve_count)
            
        # log the retrieved articles
        try:
            self.logger.info(f"Retrieved {len(docs)} documents")
            for i, doc in enumerate(docs):
                self.logger.info(f"Document {i}: {doc["metadata"]['title']}")
        except Exception as e:
            self.logger.error(f"Error logging documents: {str(e)}")
            self.logger.info(f"Retrieved documents {docs}")
            
            
        if parse_result["web_search_required"]:
            web_search_docs = self.web_search(parse_result["web_search_phrase"])

            selected_articles = self.select_articles(docs, query, web_search_docs=web_search_docs, recommended_news_ids=recommended_news_ids)
        else:
            selected_articles = self.select_articles(docs, query, recommended_news_ids=recommended_news_ids)
        
        
        # generate a short answer for user's query based on thh selected summary
        agent_context = (
            f"You are a news recommendation expert. Your task is to curate news articles to answer user's query."
            f"You will be provided with the user's query and {retrieve_count} articles ."
            f"Your task is to generate a short answer that summarizes the selected articles to answer user's query. "
            f"Your output should be structured as follows:"
            f"<response>short answer</response>"
        )
        
        # TODO: use rephrased query instead of raw query
        article_string = self.generate_article_prompt(selected_articles)
        prompt = (
            f"user_query='{query}'."
            f"articles:\n{article_string}"            
        )
        
        summary = self.model.get_model_response(prompt, context=agent_context)
        summary = re.search(r"<response>(.*?)</response>", summary).group(1)
        
        
        articles_with_bookmarks = self.bookmark_db.add_bookmark_status(selected_articles, user_id, workspace_id)
        
        response = {
            "articles": articles_with_bookmarks,
            "summary": summary
        }
        
        # self.logger.info(f"Generated response: {response}")
        return response

    # recommend news to users based on their interests and maintain diversity
    def daily_recommendation(self, user_id, workspace_id):
        # get top 10 tags the user likes
        top_tags = self.interest_db.get_top_tags(user_id=user_id, workspace_id=workspace_id, tag_count=10) 
        
        # do rag search based on the tags
        docs = self.db.similarity_search(" ".join(top_tags), n_results=10)
        
        self.logger.info(f"Retrieved {len(docs)} documents: {docs}")
        
        # use LLM to ensure diversity and select top 3 articles
        
        # for now, select the top 3 articles directly from RAG results
        selected_articles = docs[:3]
        
        context = ""
        for i, doc in enumerate(selected_articles):
            context += (
                f"Article {i}:\n"
                f"- Title: {doc["metadata"]["title"]}\n"
                f"- Content: {doc["page_content"]}\n\n"
            )
            self.logger.info(f"Selected article {i}: {doc['metadata']['title']}")
        
        # generate response
        prompt = (
            f"Generate a short summary in 60 words for the following articles:\n\n"
            f"{context}"
            f"Return your response as a single sentence wrapped in <response> tags, formatted exactly as '<response>Short answer here.</response>'. "
        )
        
        summary = self.model.get_model_response(prompt)
        summary = re.search(r"<response>(.*?)</response>", summary).group(1)
        
        # add a greeting message
        summary = "Good news! Here are some articles you may like:\n" + summary
        
        # add bookmark status to articles
        articles_with_bookmarks = self.bookmark_db.add_bookmark_status(selected_articles, user_id, workspace_id)
        
        response = {
            "articles": articles_with_bookmarks,
            "summary": summary
        }
        
        # self.logger.info(f"Generated response: {response}")
        return response

    
if __name__ == "__main__":
    rag = RAG()
    response = rag.generate_response("Any cool mobile games coming up this week?", rag_mode="rephrased_query")
    self.logger.info(response)
    
    
