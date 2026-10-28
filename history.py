chat_history = []


def add_message(role, text):
    chat_history.append((role, text))


def get_history():
    return chat_history[-10:]