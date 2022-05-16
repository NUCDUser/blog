import re


def estimate_reading_time(text):
    words = len(re.findall(r'\w+', text))
    
    
#TODO CREATE NEWSLETTER PROCESSOR
    