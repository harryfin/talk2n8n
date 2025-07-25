class Conversation:
    """Conversation class to manage a chat conversation. It handles user messages and assistant responses."""
    def __init__(self):
        self.conversation_history = []

    def add_user_message(self, message):
        """Add a user message to the conversation history."""
        self.conversation_history.append({"role": "user", "content": message})

    def add_assistant_response(self, response):
        """Add an assistant response to the conversation history."""
        self.conversation_history.append({"role": "assistant", "content": response})

    def get_conversation_history(self):
        """Return the conversation history as text."""
        return "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in self.conversation_history
        )

    def remove_last_message(self):
        """Remove the last message from the conversation history."""
        if self.conversation_history:
            self.conversation_history.pop()
