from pydantic import BaseModel

class BasicResponse(BaseModel):
    """
    A class for a simple string response from the LLM.
    """
    response: str
