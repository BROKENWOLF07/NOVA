import google.generativeai as genai
import os
from dotenv import load_dotenv
from history import add_message, get_history

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# Try this model first
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def ask_ai(question):

    add_message("user", question)

    history = get_history()

    context = ""

    for role, text in history:
        context += f"{role}: {text}\n"

    try:

        prompt = f"""
You are Nova, an intelligent personal AI assistant.

Your personality:
- Friendly
- Helpful
- Patient
- Professional
- Good at teaching beginners

Keep responses concise and natural.
Address the user as sir.
Act like a real personal assistant.

Conversation history:
{context}

User:
{question}
"""

        response = model.generate_content(prompt)

        answer = response.text

        add_message("assistant", answer)

        return answer

    except Exception as e:

        return f"AI Error: {e}"