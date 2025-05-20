import dotenv
import os
from openai import AzureOpenAI
from ..utils.Logger import setup_logger 


class USTModelClient:
    def __init__(self):
        self.logger = setup_logger("USTModel", stream=False)
        self.client = AzureOpenAI(
            azure_endpoint="https://hkust.azure-api.net",
            api_key=os.getenv("UST_API_KEY"),
            api_version="2025-02-01-preview"
        )
        self.logger.info("USTModelClient initialized")

    def get_model_response(self, prompt, context=None):
        messages = []
        if context:
            messages.append({"role": "user", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        self.logger.info(f"Sending prompt to UST model: {prompt}")
        
    
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        try:
            self.logger.info(f"\n=======\n[Prompt] {prompt}\n\n[Response] {response}")
        except Exception as e:
            self.logger.error(f"Error logging response: {e}")
        
        self.logger.info(f"Received response from UST model")
        
        return response.choices[0].message.content
