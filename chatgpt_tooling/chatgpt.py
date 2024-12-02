import os

from pydantic import BaseModel
from openai import OpenAI

from .structured_output.basic_response import BasicResponse
from .tool_calls.tool import Tool
from .prompt import Prompt

class ChatGPT:
    """
    The ChatGPT wrapper class, which implements chat completion with structured output
    and (optionally) tool calls.
    """
    def __init__(self, model_name: str = 'gpt-4o-mini'):
        """
        fyi: `gpt-3.5-turbo` doesn't support structured output, which will throw an error
        with this code.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is not None, "OPENAI_API_KEY environment variable must be set"
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def ask(
            self,
            prompt: Prompt, # Will modify in place.
            response_format: type[BaseModel] = BasicResponse,
            tool: Tool | None = None,
            depth: int = 0,
            debug: bool = False,
    ) -> BaseModel:
        """
        Sends a prompt to ChatGPT and then runs any given tool calls.
        IF TOOL CALLS ARE RUN, ChatGPT IS CALLED AGAIN with the response from the tool call(s),
        allowing ChatGPT to run more complex operations.
        This recursion is capped by `depth` to prevent ChatGPT from calling itself too many times.
        """
        assert depth < 10, "Depth limit reached"
        if debug:
            print(f"[debug:chatgpt ({depth=})] asking:")
            for message in prompt.messages:
                print(f"  - {message=}")
        try:
            if tool is None:
                response = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=prompt.messages,
                    response_format=response_format,
                    temperature=0.0,
                )
            else:
                response = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=prompt.messages,
                    response_format=response_format,
                    tools=tool.render_tool_descriptors() if tool else None,
                    tool_choice="auto" if tool else None,
                    temperature=0.0,
                )
        except Exception as e:
            print("HERE ARE THE MESSAGES THAT LED TO THE ERROR:")
            for message in prompt.messages:
                print(f"  - {message=}")
            raise e
        message = response.choices[0].message
        if debug:
            print(f"[debug:chatgpt ({depth=})] response: {message=}")
        if not message.tool_calls:
            prompt.messages.append({
                "role": "assistant",
                "content": message.content,
            })
            return message.parsed
        # We have tool calls!
        prompt.messages.append(message) # Tool message must immediately follow a message containing "tool_calls".
        for tool_call in message.tool_calls:
            prompt.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "function_name": tool_call.function.name,
                "content": tool.call(
                    function_name=tool_call.function.name,
                    kwargs=tool_call.function.parsed_arguments,
                    debug=debug,
                ),
            })
        return self.ask(
            prompt=prompt,
            response_format=response_format,
            tool=tool,
            depth=depth+1,
            debug=debug,
        )
