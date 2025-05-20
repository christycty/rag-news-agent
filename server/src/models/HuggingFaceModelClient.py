import os
import dotenv

import torch
import transformers
from transformers import pipeline

from ..utils.Logger import setup_logger 

model_logger = setup_logger("hfmodel", "hfmodel", stream=False)

class HuggingFaceModelClient:
    def __init__(self, model_name="gemma"):
        
        self.model_name = model_name
        if self.model_name == "gemma":
            model_card_name = "google/gemma-3-12b-it"
            
            self.model = pipeline(
                "text-generation",
                model=model_card_name,
                device=0 if torch.cuda.is_available() else -1,
                token=os.getenv("HF_TOKEN"),
            )
            
            
        elif self.model_name== "nemotron":
            model_card_name = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
            model_kwargs = {"torch_dtype": torch.bfloat16, "device_map": "auto"}
            tokenizer = transformers.AutoTokenizer.from_pretrained(model_card_name)
            tokenizer.pad_token_id = tokenizer.eos_token_id
            
            self.model = pipeline(
                "text-generation",
                model=model_card_name,
                # model_kwargs=model_kwargs,
                tokenizer=tokenizer,
                do_sample=False
            )
    
    def get_model_response(self, prompt):
        if self.model_name == "gemma":
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a news curator that summarizes news articles."}]
                },
                {
                    "role": "user", 
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
            
            try:
                with torch.no_grad():
                    response = self.model(messages, max_new_tokens=5000)
                    
                model_logger.info(f"\n=======\n[Prompt] {prompt}\n\n[Response] {response}")
            except Exception as e:
                model_logger.error(f"Error in HuggingFaceModelClient: {e}")
                return None
            
            text = response[0]['generated_text'][-1]["content"]
            torch.cuda.empty_cache()
            
        elif self.model_name == "nemotron":
            messages = [
                {"role": "system", "content": "detailed thinking off"},
                {"role": "user", "content": prompt}
            ]
            try:
                with torch.no_grad():
                    response = self.model(messages, max_length=5000)
                    
                model_logger.info(f"\n=======\n[Prompt] {messages}\n\n[Response] {response}")
            except Exception as e:
                model_logger.error(f"Error in HuggingFaceModelClient: {e}")
                return None
            text = response[0]["generated_text"][-1]["content"]
            # text = response[0]['generated_text']
            torch.cuda.empty_cache()
        return text

    def clear(self):
        # clear the model
        del self.model
        torch.cuda.empty_cache()
        