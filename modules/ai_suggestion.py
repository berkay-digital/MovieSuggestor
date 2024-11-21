from g4f import ChatCompletion
import os
from openai import OpenAI
import time
import threading
from queue import Queue

def get_openai_suggestion(user_input, system_prompt):
    try:
        print("Using OpenAI GPT-4...")
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="gpt-4",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {str(e)}")
        return None

def g4f_worker(system_prompt, user_input, result_queue):
    try:
        response = ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        result_queue.put(response)
    except Exception as e:
        print(f"g4f error: {str(e)}")
        result_queue.put(None)

def get_g4f_suggestion(system_prompt, user_input):
    try:
        print("Using g4f (Free GPT-4)...")
        result_queue = Queue()
        worker_thread = threading.Thread(
            target=g4f_worker,
            args=(system_prompt, user_input, result_queue)
        )
        worker_thread.daemon = True
        worker_thread.start()
        
        # Wait for result with timeout
        worker_thread.join(timeout=10)
        
        # If thread is still alive after timeout
        if worker_thread.is_alive():
            print("g4f timed out after 10 seconds")
            return None
            
        # Get result if available
        if not result_queue.empty():
            return result_queue.get()
        return None
        
    except Exception as e:
        print(f"g4f error: {str(e)}")
        return None

def get_ai_suggestion(user_input):
    system_prompt = """You are a knowledgeable movie and TV show recommendation assistant. 
    Format your responses with:
    - Use '**' for important titles or key points
    - Use '*' for emphasis on genres or themes
    - Use clear paragraphs with line breaks
    - Keep responses concise but informative
    - Include 2-3 specific recommendations with brief explanations
    - Mention similar titles if relevant"""

    # Try g4f first
    result = get_g4f_suggestion(system_prompt, user_input)

    # If g4f fails, try OpenAI
    if result is None:
        result = get_openai_suggestion(user_input, system_prompt)

    if result:
        return f"""{result}
        
Feel free to ask for more specific recommendations!"""

    return "I apologize, but I encountered an error while processing your request. Please try again."

# You can run this file to test the AI suggestion
if __name__ == "__main__":
    user_input = "I want to watch a movie about a detective solving a murder mystery."
    suggestion = get_ai_suggestion(user_input)
    print(suggestion)
