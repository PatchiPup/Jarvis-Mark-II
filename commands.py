from tasks import add_task
from command_modules_init import all_commands

def extract_content(response, i):
    j = response.find(")", i)
    if j != -1:
        return response[i+4:j], j
    return None, i

def process_command(response):
    """
    Parse the LLM response for embedded command tokens.
    Schedule actions via add_task and return the cleaned response text and any sound effects.
    """
    clean_response = []
    i = 0
    length = len(response)

    while i < length:
        if response[i:i+3] in all_commands and response[i+3] == '(':
            command = response[i:i+3]
            handler = all_commands[command]
            content, j = extract_content(response, i)
            if content is not None:                    
                method, args = handler(content)
                add_task(method, args)                
                i = j
        else:
            clean_response.append(response[i])
        i += 1

    return "".join(clean_response).strip()
