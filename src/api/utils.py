"""
Utility functions for API operations
"""

def extract_clean_answer(result):
    """
    Extract the clean answer from the SQL Agent's response.
    
    The SQL Agent returns complex nested structures, but we want just the readable answer.
    This function handles various response formats and extracts the clean content.
    """
    if hasattr(result, 'content'):
        # If it's a message object with content
        return result.content
    elif isinstance(result, dict):
        # If it's a dictionary, look for the answer
        if 'answer' in result:
            return result['answer']
        elif 'output' in result:
            return result['output']
        elif 'result' in result:
            # Handle nested result structures
            nested_result = result['result']
            if isinstance(nested_result, dict) and 'answer' in nested_result:
                return nested_result['answer']
            else:
                return str(nested_result)
        else:
            return str(result)
    elif isinstance(result, str):
        return result
    else:
        return str(result)
