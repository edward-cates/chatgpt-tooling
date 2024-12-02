from pydantic import BaseModel, Field

class ToolArgument(BaseModel):
    """
    A class to abstract and simplify desribing an argument to a tool_call function.
    """
    name: str = Field(description="The name of the argument.")
    description: str = Field(description="A description of the argument.")
    type: str = Field(description="The type of the argument (e.g. `str`, `int`, `float`, `list[str]`).")
    enum: list[str] | None = Field(description="An optional list of allowed values for the argument (e.g. `['yes', 'no']`).")

    def render(self) -> dict:
        if "list" in self.type:
            return self._render_list_type()
        if "dict" in self.type:
            raise NotImplementedError(f"Dict types not yet supported.")
        to_return = {
            "type": self._transform_python_type_to_openai_type(self.type),
            "description": self.description,
        }
        if self.enum:
            to_return["enum"] = self.enum
        return to_return
    
    def _render_list_type(self) -> dict:
        """
        `type` is `list[<subtype>]`.
        """
        open_bracket_index = self.type.index("[")
        close_bracket_index = self.type.index("]")
        subtype = self.type[open_bracket_index + 1:close_bracket_index]
        return {
            "type": "array",
            "items": {
                "type": self._transform_python_type_to_openai_type(subtype),
            },
        }

    @staticmethod
    def _transform_python_type_to_openai_type(python_type: str) -> str:
        """
        Transforms a python type to an openai type.
        If the type is not found in the mapping, it is returned as is.
        """
        type_map = {
            "int": "integer",
            "float": "number",
            "str": "string",
        }
        return type_map.get(python_type, python_type)
