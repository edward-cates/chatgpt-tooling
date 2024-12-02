from pydantic import BaseModel, Field

class BasicResponse(BaseModel):
    """
    A class for a simple string response from the LLM.
    """
    response: str = Field(description="A text response from the LLM.")
