import re
import ast

def modify_text_for_llm(title, subtitle, content):
    """
    Modify the text to be used in the LLM prompt. This function will add a title, subtitle, and content to the 
    prompt text.
    
    Args:
        title (str): The title of the article.
        subtitle (str): The subtitle of the article.
        content (str): The content of the article.
    
    Returns:
        str: The modified text to be used in the LLM prompt.
    """    
    return f"##Título:\n{title}\n##Subtítulo:\n{subtitle}\n##Contenido:\n{content}"


def parser_json_response_llm(test_answer_string):
    if not test_answer_string:
        return None
    try:
        json_string = test_answer_string.replace("'", '"')
        json_string = json_string.replace(",}", "}")
        json_string = re.sub(r',\s*}', '}', json_string)

        json_start_index = json_string.find('{')
        json_string = json_string[json_start_index:]
        json_end_index = json_string.rfind('}') + 1
        json_string = json_string[:json_end_index]
        json_object = ast.literal_eval(json_string)

        for key, value in json_object.items():
            if isinstance(value, str):
                try:
                    json_object[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass 

        return json_object
    
    except SyntaxError as e:
        print(f"Error decoding JSON: {e}\nResponse string: {test_answer_string}")
        return None
    
    except ValueError as e:
        print(f"Error decoding JSON: {e}\nResponse string: {test_answer_string}")
        return None
    
def validate_json_llm(json_response, attribute_dict):
    """
    Check if the JSON response is valid based on the attribute dictionary. The dict will specify the keys to have, 
    and the type of value they should have. If the expected value of the field is a list, this is determined either 
    by the presence of square brackets in the string, or by whether the value can be split by commas into a list.
    
    Args:
        json_response (dict): The JSON object to validate. comes from an LLM response
        attribute_dict (dict): A dictionary describing the expected keys and their value types. Value types can be 
                               types like int, str, float, list, or any callable that returns a boolean indicating 
                               type validity.

    Returns:
        bool: True if the JSON matches the expected format, False otherwise.
    """
    if not json_response:
        return None
    
    json_response_keys_upper = set(key.upper() for key in json_response.keys())
    attribute_dict_keys_upper = set(key.upper() for key in attribute_dict.keys())
    
    # Check if all expected keys are in the JSON and the number of keys match
    if json_response_keys_upper != attribute_dict_keys_upper:
        return None
 
    # Validate each key in the JSON
    for key, expected_type in attribute_dict.items():
        value = json_response.get(key)
        if expected_type is list:
            if value is None:
                value = []
            
            elif isinstance(value, str):
                # Try to interpret strings as lists if they are in brackets or can be split by commas
                if value.startswith('[') and value.endswith(']'):
                    try:
                        value = eval(value)
                    except:
                        return None
                else:
                    # Split by comma to form a list if no brackets but contains commas
                    value = [v.strip() for v in value.split(',') if v.strip()]
            json_response[key] = value
     
    return json_response
