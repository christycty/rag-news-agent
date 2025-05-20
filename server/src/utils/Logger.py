import os
import sys
import logging

def setup_logger(name, log_name=None, stream=True, level=logging.INFO):
    
    if log_name is None:
        log_name = name
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    cur_path = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(cur_path, '../../logs')
    
    file_handler = logging.FileHandler(f'{log_dir}/{log_name}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger