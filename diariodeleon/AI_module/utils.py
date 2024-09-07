import json

def parser_json_response_llm(test_answer_string):
    try:
        json_string = test_answer_string.replace("'", '"')
        json_start_index = json_string.find('{')
        json_string = json_string[json_start_index:]
        json_end_index = json_string.rfind('}') + 1
        json_string = json_string[:json_end_index]
        # Parse the JSON string
        json_object = json.loads(json_string)

        for key, value in json_object.items():
            if value in ['True', 'False', 'None']:
                json_object[key] = eval(value)

        return json_object
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}\nResponse string: {test_answer_string}")
    
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

    # Check if all expected keys are in the JSON and the number of keys match, else return False
    if set(json_response.keys().upper()) != set(attribute_dict.keys().upper()):
        return False

    # Validate each key in the JSON
    for key, expected_type in attribute_dict.items():
        value = json_response.get(key)
        if expected_type is list:
            if value in None:
                value = []
            
            elif isinstance(value, str):
                # Try to interpret strings as lists if they are in brackets or can be split by commas
                if value.startswith('[') and value.endswith(']'):
                    try:
                        value = eval(value)
                    except:
                        return False
                else:
                    # Split by comma to form a list if no brackets but contains commas
                    value = [v.strip() for v in value.split(',') if v.strip()]
            json_response[key] = value
     
    return json_response