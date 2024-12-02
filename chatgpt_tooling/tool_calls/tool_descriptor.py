from pydantic import BaseModel, Field

from .tool_argument import ToolArgument

class ToolDescriptor(BaseModel):
    name: str = Field(description="The name of the tool.")
    description: str = Field(description="A description of the tool.")
    arguments: list[ToolArgument] = Field(description="A list of arguments to the tool.")

    def render(self) -> dict:
        """
        Abstracts building OpenAI's complicated tool description object.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        arg.name: arg.render()
                        for arg in self.arguments
                    },
                    "required": [
                        arg.name for arg in self.arguments
                    ],
                    "additionalProperties": False,
                }
            }
        }
