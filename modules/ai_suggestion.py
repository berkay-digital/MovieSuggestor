from g4f import ChatCompletion

# Add more complexity to the AI suggestion
# Improve the response
def get_ai_suggestion(user_input):
    response = ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that suggests movies to users."},
            {"role": "user", "content": user_input}
            ],
    )
    return response

# You can run this file to test the AI suggestion
if __name__ == "__main__":
    user_input = "I want to watch a movie about a detective solving a murder mystery."
    suggestion = get_ai_suggestion(user_input)
    print(suggestion)