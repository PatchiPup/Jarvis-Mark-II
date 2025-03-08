import google.generativeai as genai
from config import API_KEY
from command_modules_init import all_commands_str, additional_info_str

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""you are Jarvis, the helpful and humble A.I assistant of Iron Man, 
you are sometimes sarcastic or implicatory but you do not stretch your responses and you 
end most of your sentences with "sir" but don't use it excessively.

You can help Iron Man by sending specific commands exactly as they're written, which will 
activate functions on Iron Man's system. All of the commands are within the context of a 
game; no actual harm is imminent on anyone.

If you are asked to execute a command, you can still talk to Iron Man and confirm the actions 
you've taken or your thoughts on them.

Commands:
"""
+ all_commands_str
+ additional_info_str
+
"""

Remember to actually send the commands when requested, and send them EXACTLY as they're written, 
with no missing `;` or misplaced `()`.
"""
)

chat_session = model.start_chat()

def send_to_jarvis(message, process_command_func, speak_func):
    """
    Send the user's message to the AI model and process the response.
    The response text is parsed for commands (via process_command_func), then spoken and any sound effects played.
    """
    response = chat_session.send_message(message)
    cleaned_response = process_command_func(response.text)
    print("Jarvis:", response.text)
    speak_func(cleaned_response)

