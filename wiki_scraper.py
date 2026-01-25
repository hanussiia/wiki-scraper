import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from pathlib import Path


WIKI = "https://bulbapedia.bulbagarden.net/wiki/"

class WikiScraper:
    def __init__(self):
        pass

class Parser:
    def __init__(self):
        pass

def validation(parser, args):
    if args.number is not None and args.number <= 0:
        parser.error("--number must be > 0")

    if args.table and len(args.table) > 20:
        parser.error("--table must be <= 20 chars")

    if args.count_words and len(args.count_words) > 20:
        parser.error("--count-words must be <= 20 chars")

    if args.summary and len(args.summary) > 20:
        parser.error("--summary must be <= 20 chars")

    if (args.table and not args.number) or (args.number and not args.table):
        parser.error("--table argument must always be with --number")

def parsing(): 
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--summary", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to summarize at wiki, length <= 20 chars", dest="summary")
    mode.add_argument("--table", type=str, nargs="?", const="Type", help="paste the fraze you want to get table from wiki, length <= 20 chars", dest="table")
    mode.add_argument("--count-words", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to get table from wiki, length <= 20 chars", dest="count_words")

    parser.add_argument("--number", type=int, help="table number (required with --table)")
    parser.add_argument("--first-row-is-header", action="store_true", help="treat first row as header")
    
    args = parser.parse_args()
    validation(parser, args)

    return args

def making_request(fraze: str):
    fraze_changed = fraze.replace(" ", "_")
    response = requests.get(WIKI + fraze_changed)
    return response

def summary(summary_name):
    response = making_request(summary_name)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.select_one('p').text.strip()
    print(paragraphs)

def what_task(args):
    if args.summary:
        summary(args.summary)
    elif args.table:
        table(args.table, args.number, args.first_row_is_header)
    elif args.count_words:
        count_words(args.count_words)

def count_words_table(df):
    counted_df = df.stack().value_counts().reset_index()
    counted_df.columns = ["value", "count"]
    return counted_df

def table(table_name, number, first_row_is_header):
    response = making_request(table_name)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        print("No tables found")
        return
    
    if number > len(tables):
        print("Table number out of range, so the last possible table is used")
        number = len(tables)
    
    table_to_use = tables[number - 1]
    rows = table_to_use.find_all('tr')
    data = []

    for row in rows:
        #TODO problem when double th in a row
        cells = row.find_all(['td', 'th']) #TH is used for table header cells while TD is used for table data cells
        row_data = [cell.get_text(strip=True) for cell in cells]
        if row_data: 
            data.append(row_data)
    print(data)
    df = pd.DataFrame(data)
    print(df)
    df = df.dropna(thresh=len(df)*0.9, axis=1)
    df = df.dropna(thresh=len(df.columns)*0.9, axis=0)

    df_without_header = df.drop(df.index[0]).reset_index(drop=True)
    if first_row_is_header:
        df.columns = df.iloc[0]
        print(df.columns)
        df = df_without_header
    
    if df is not None:
        print(df)
    
    # --- zapis do pliku ---
    filename = table_name.replace(" ", "_") + ".csv"
    df.to_csv(filename, index=False)
    print(f"Table saved to {filename}")

    df_counted_words = count_words_table(df_without_header)
    print(df_counted_words)

def get_article_text(soup):
    content_div = soup.find("div")

    if content_div is None:
        return ""

    paragraphs = content_div.find_all("p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs)

    return text

def extract_words(text):
    return re.findall(r"[a-zA-Z]+", text.lower())

def load_word_counts(path="word-counts.json"):
    if not Path(path).exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_word_counts(counts, path="word-counts.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=2, ensure_ascii=False)


def update_word_counts(global_counts, words):
    for word in words:
        if word in global_counts:
            global_counts[word] += 1
        else:
            global_counts[word] = 1

    return global_counts

def count_words(fraze):
    response = making_request(fraze)
    soup = BeautifulSoup(response.text, "html.parser")

    article_text = get_article_text(soup)
    if not article_text:
        print("No article text found")
        return

    words = extract_words(article_text)

    global_counts = load_word_counts()
    global_counts = update_word_counts(global_counts, words)
    global_counts = dict(sorted(global_counts.items(), key=lambda item: item[1], reverse=True))

    save_word_counts(global_counts)

    print(f"Counted {len(words)} words from article '{fraze}'")

def main():
    scraper = WikiScraper()
    parser = Parser()
    args = parsing()

    what_task(args)
    #TODO artykul nie jest dostepny -> co wtedy?

if __name__ == "__main__":
    main()