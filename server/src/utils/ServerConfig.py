""" ServerConfig.py
This module is responsible for loading and managing the server configuration.
"""

import os
import ast
import uuid
import json 

from .Logger import setup_logger

class ServerConfig:
    def __init__(self):        
        self.logger = setup_logger("config")
        
        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(cur_path, '../config.json')
        self.load_config()
        
    def load_config(self):
        # load profile
        try:
            self.config = json.load(open(self.config_path, 'r'))
            self.logger.info(f"Loaded server configuration: {self.config}")
            
            self.tags = self.config["tags"]
            self.query = self.config["query"]
            
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")

    def get_config(self):
        # return all config for json response
        return self.config
    