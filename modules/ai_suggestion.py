from g4f import ChatCompletion
import os
from openai import OpenAI
import time
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    # Set the signal handler and a timeout
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

def get_openai_suggestion(user_input, system_prompt):
    try:
        print("Using OpenAI GPT-4...")
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            message=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="gpt-4o-mini",
        )

        return chat_completion.coices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {str(e)}")
        return None

def get_g4f_suggestion(system_prompt, user_input):
    try:
        print("Using g4f (Free GPT-4)...")
        with timeout(10): # 10 sec timeout setting
            response = ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
            )
            return response
    except TimeoutException:
        print("G4f timed out after 10 seconds")
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
