import os
import sys
import re
from openai import OpenAI


AI_MODULE_PATH = str(os.getenv("AI_MODULE_PATH", "/home/adrian.alvarez/Projects/diariodeleon-scraper/diariodeleon/AI_module"))
sys.path.append(AI_MODULE_PATH)



from typing import Optional  # Import the Optional class for nullable parameters

from utils import parser_json_response_llm, validate_json_llm


class Prompt(): 
    def __init__(self, system_msg, user_msg):
        self.system_msg = system_msg
        self.user_msg = user_msg

    def format_usr_msg(self, **kwargs) -> str:
        return self.user_msg.format(**kwargs)
    
    def format_system_msg(self, **kwargs) -> str:
        return self.system_msg.format(**kwargs)
    
    def extract_required_json_output(self):
        # Define the pattern to capture the dictionary-like structure in the text
        dict_pattern = r"({[^}]+})"

        # Search for the dictionary structure in the given text
        match = re.search(dict_pattern, self.system_msg, re.DOTALL)

        if match:
            dict_str = match.group(0).replace("\n", "").replace("  ", " ").strip()
            try:
                python_dict = eval(dict_str)
                for key in python_dict.keys():
                    if "list" in python_dict[key]:
                        python_dict[key] = list
                    else:
                        python_dict[key] = str
                return python_dict

            except SyntaxError as e:
                print(f"Error parsing dictionary: {e}")
                return None
        else:
            print("No dictionary structure found in the text.")
            return None

        

class NewsParser():
    def __init__(self, api_key, prompt: Prompt, max_retries=3, model="gpt-4o-2024-08-06"):
        self.api_controller = OpenAIAPI(api_key, model)
        self.max_retires = max_retries
        self.prompt = prompt
        self.expected_attributes_dict = prompt.extract_required_json_output()
    
    
    def analize_news(self, article_text: str) -> dict:
        # Creating a new Prompt instance based on the controller
        system_msg = self.prompt.system_msg
        
        user_msg = self.prompt.format_usr_msg(article_text=article_text)
        for attempt in range(self.max_retires):
            response= self.api_controller.get_metrics(system_msg, user_msg)
            json_response = parser_json_response_llm(response)
            validated_response = validate_json_llm(json_response, self.expected_attributes_dict)
            if validated_response:
                return validated_response
        return None


class OpenAIAPI():
    def __init__(self, api_key, model = "gpt-4o-2024-08-06"):
        self.client= OpenAI(
            api_key = api_key
        )
        self.model = model

    def format_prompt(self,system_msg, user_msg):
        messages=[{"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}]
        return messages
    
    def get_metrics(self, system_msg, user_msg):
        messages = self.format_prompt(system_msg, user_msg)
        response_format={"type": "json_object" }
        
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages,response_format=response_format)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error extracting attributes: {e}")
            return None  