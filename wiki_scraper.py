import argparse
import requests
from bs4 import BeautifulSoup

WIKI = "https://bulbapedia.bulbagarden.net/wiki/"

class WikiScraper:
    def __init__(self):
        pass

class Parser:
    def __init__(self):
        pass

def parsing(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=str, default="Team Rocket", help="paste the fraze you want to summarize at wiki, length <= 20 chars", dest="summary")

    args = parser.parse_args()
    return args

def making_request(fraze: str):
    fraze_changed = fraze.replace(" ", "_")
    response = requests.get(WIKI + fraze_changed)
    return response

def main():
    scraper = WikiScraper()
    parser = Parser()
    args = parsing()

    if args.summary and len(args.summary) <= 20:
        response = making_request(args.summary)
    else:
        print("Invalid input or summary too long")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.select_one('p').text.strip()
    print(paragraphs)
    #artykul nie jest dostepny -> co wtedy?

if __name__ == "__main__":
    main()