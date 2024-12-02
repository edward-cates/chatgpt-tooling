from abc import ABC
import traceback

from pydantic import BaseModel, ConfigDict

from .tool_descriptor import ToolDescriptor
from .tool_argument import ToolArgument

class Tool(BaseModel, ABC):
    """
    A abstract class for a tool class to inherit.

    Usage:
        class MyTool(Tool):
            @property
            def method_descriptor(self) -> ToolDescriptor:
                return ToolDescriptor(name="method", description="method description", arguments=[
                    ToolArgument(name="arg1", description="arg1 description", type="str"),
                    ToolArgument(name="arg2", description="arg2 description", type="int"),
                ])
            def method(self, arg1: str, arg2: int) -> str:
                return "method response"

    When calling the LLM, attributes (or properties) ending with `_descriptor` are used
    to describe the available tool calls (aka methods).

    When the LLM responds with tool calls (aka function names and arguments), the
    `call` method is used to call that method.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def tool_descriptors(self) -> list[ToolDescriptor]:
        return [
            getattr(self, attr) for attr in dir(self)
            if attr.endswith("_descriptor")
        ]

    def render_tool_descriptors(self) -> list[dict]:
        return [tool.render() for tool in self.tool_descriptors]

    def call(self, function_name: str, kwargs: dict, debug: bool) -> str:
        if debug or True:
            print(f"[debug:chatgpt:tools] calling {function_name} with {kwargs=}")
        callable_function = getattr(self, function_name)
        try:
            # replace square brackets with parentheses
            return str(callable_function(**kwargs)).replace("[", "(").replace("]", ")")
        except Exception as e:
            # print traceback
            traceback.print_exc()
            # print(f"[debug:chatgpt:tools] error: {e}")
            return str(e)
