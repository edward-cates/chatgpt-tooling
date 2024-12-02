from pydantic import BaseModel
import tiktoken

class Prompt(BaseModel):
    """
    A class to build and manage a prompt for a chat completion,
    passed to the LLM and used to store the entire chat.

    Usage:
        prompt = Prompt()
        prompt.add("system", "You are a helpful assistant.")
        prompt.add("user", "What is the capital of France?")
    """

    messages: list[dict[str, str]] = []

    def add(self, role: str, content: str):
        """
        Add a message to the prompt.
        LLM responses are automatically added using this method.
        """
        assert isinstance(role, str), f"Invalid role: {role=}, must be a string"
        assert isinstance(content, str), f"Invalid content: {content=}, must be a string"
        valid_roles = {'system', 'assistant', 'user', 'function', 'tool'}
        assert role in valid_roles, f"Invalid role: {role=}, must be in {valid_roles=}"
        self.messages.append({"role": role, "content": content})

    def count_tokens(self) -> int:
        """
        A helper, method to count the number of tokens in the prompt.
        Not used by the LLM, just here in case you need it.
        """
        encoding = tiktoken.encoding_for_model("gpt-4o")
        text = str(self.messages)
        return len(encoding.encode(text))

