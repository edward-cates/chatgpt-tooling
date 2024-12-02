import argparse
import json
import random

from pydantic import BaseModel, Field

from chatgpt_tooling import (
    ChatGPT,
    Prompt,
    Tool,
    ToolDescriptor,
    ToolArgument,
)

class CoinFlippingTool(Tool):
    history: list[str] = Field(default_factory=list, description="The history of coin flips.")

    @property
    def flip_coin_descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            name="flip_coin",
            description="Flip a coin and save the result. Requires the probability of heads as an argument.",
            arguments=[
                ToolArgument(
                    name="probability_of_heads",
                    description="The probability of heads (between 0 and 1).",
                    type="float",
                    enum=None,
                ),
            ],
        )
    def flip_coin(self, probability_of_heads: float) -> str:
        assert 0 <= probability_of_heads <= 1, f"Probability of heads must be between 0 and 1 but got {probability_of_heads=}"
        result = "heads" if random.random() < probability_of_heads else "tails"
        self.history.append(result)
        return result

class CoinFlipResponse(BaseModel):
    wasHeads: bool = Field(description="Whether the coin flip was heads.")

def main(debug: bool) -> CoinFlipResponse:
    prompt = Prompt()
    prompt.add("system", "You are a chatbot to facilitate the user playing a coin flipping game.")
    prompt.add("user", "Flip a coin that is always heads.")

    coin_flipping_tool = CoinFlippingTool()

    chatgpt = ChatGPT(model_name="gpt-4o-mini")

    response = chatgpt.ask(
        prompt=prompt,
        tool=coin_flipping_tool,
        response_format=CoinFlipResponse,
        debug=debug,
    )
    assert isinstance(response, CoinFlipResponse)
    print("\nRESPONSE:")
    print(
        json.dumps(response.model_dump(), indent=2),
    )
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    """
    `--debug` will print all the internal steps.
    """
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args.debug)
