from demo import main, CoinFlipResponse

def test_demo() -> None:
    response = main(debug=False)
    assert isinstance(response, CoinFlipResponse)
    assert response.wasHeads
