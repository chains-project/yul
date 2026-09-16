from api_fetcher.fetcher import ApiFetcher

def main():
    fetcher = ApiFetcher(base_url="https://jsonplaceholder.typicode.com")
    items = fetcher.get("posts", limit=5)
    for item in items:
        print(item)

if __name__ == "__main__":
    main()