import dotenv
import os

from ollama import chat

from ..utils.Logger import setup_logger 


class OllamaModelClient:
    def __init__(self, model_type="deepseek-r1"):
        self.model = model_type
        self.logger = setup_logger("OllamaModel", stream=False)
        
    def get_model_response(self, prompt):
        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.logger.info(f"\n=======\n[Prompt] {prompt}\n\n[Response] {response}")
        return response.message.content