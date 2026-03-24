# demo: how to use Arkham Client sdk to access Arkham Intelligence API

from arkham_client import ArkhamClient

def main():
    # create an instance of ArkhamClient with your API key
    client = ArkhamClient(api_key="your-api-key")

    # optionally, you can also use email and password to authenticate
    client = ArkhamClient(email="your@email.com", password="your-password")

    # get transfer list of OKX
    txs = client.transfers(base="okx", timeLast="1h", limit=10, flow="out")
    print(txs)

if __name__ == "__main__":
    main()