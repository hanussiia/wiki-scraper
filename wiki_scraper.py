import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from pathlib import Path
from wordfreq import top_n_list, zipf_frequency
import matplotlib.pyplot as plt
import numpy as np
import time


WIKI = "https://bulbapedia.bulbagarden.net/wiki/"

class WikiScraper:
    def __init__(self):
        pass

class Parser:
    def __init__(self):
        pass

def validation(parser, args): 
     # --- TABLE ---
    if args.table:
        if not args.number:
            parser.error("--table requires --number")
        if args.number <= 0:
            parser.error("--number must be > 0")

    # --- ANALYSIS ---
    if args.analyze_relative:
        if not args.mode or not args.count: #mozna nie prowerat tak kak jest default znaczenia
            parser.error(
                "--analyze-relative-word-frequency requires --mode and --count"
            )
        if args.count <= 0:
            parser.error("--count must be > 0")
    
    # --- AUTO COUNT WORDS ---
    if args.auto_count_words:
        if args.depth <= 0 or args.wait <= 0:
            parser.error("--depth and --wait must be > 0")

    # --- TEXT LENGTH ---
    for arg in [args.summary, args.table, args.count_words, args.analyze_relative, args.auto_count_words]:
        if arg and len(arg) > 20:
            parser.error("article name must be <= 20 characters")

def parsing(): 
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--summary", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to summarize at wiki, length <= 20 chars", dest="summary")
    mode.add_argument("--table", type=str, nargs="?", const="Type", help="paste the fraze you want to get table from wiki, length <= 20 chars", dest="table")
    mode.add_argument("--count-words", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to count words frequency from wiki article, length <= 20 chars", dest="count_words")
    mode.add_argument("--analyze-relative", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to compare with language word frequency, length <= 20 chars", dest="analyze_relative")
    mode.add_argument("--auto-count-words", type=str, nargs="?", const="Team Rocket", help="paste the fraze you want to count words frequency from wiki article and phrases in all related links, length <= 20 chars", dest="auto_count_words")

    parser.add_argument("--number", type=int, help="table number (required with --table)")
    parser.add_argument("--first-row-is-header", action="store_true", help="treat first row as header")

    parser.add_argument("--mode", type=str, choices=["article", "language"], default="article", help="mode: article or language (default: article)")
    parser.add_argument("--count", type=int, default=10, help="number of words to analyze (default: 10)")
    parser.add_argument("--chart", type=str, default=None, help="path to save chart image")

    parser.add_argument("--depth", type=int, default=2, help="depth of search (can be used only with --auto-count-words, default=2)")
    parser.add_argument("--wait", type=int, default=1, help="waiting time for the next word counts (can be used only with --auto-count-words, default=0)")


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
        soup = get_article_div_soup(args.count_words)
        count_words(args.count_words, soup)
    elif args.analyze_relative:
        analyze_relative_word_frequency(mode=args.mode, n=args.count, chart_path=args.chart)
    elif args.auto_count_words:
        auto_count_words(args.auto_count_words, depth=args.depth, t=args.wait)


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

def get_text(content_div):
    if content_div is None:
        return ""

    for br in content_div.find_all("br"):
        br.replace_with(" ")

    paragraphs = content_div.find_all("p")
    text = " ".join(" ".join(p.get_text().split()) for p in paragraphs)

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


def get_article_div_soup(phrase):
    response = making_request(phrase)
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div")


    return content_div


def count_words(phrase, soup):
    article_text = get_text(soup)

    if not article_text:
        print("No article text found")
        return

    words = extract_words(article_text)

    global_counts = load_word_counts()
    global_counts = update_word_counts(global_counts, words)
    global_counts = dict(sorted(global_counts.items(), key=lambda item: item[1], reverse=True))

    save_word_counts(global_counts)

    print(f"Counted {len(words)} words from article '{phrase}'")


def create_bar_chart(df, chart_path):
    x = np.arange(len(df))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(
        x - width / 2,
        df["frequency_art"],
        width,
        label="Article"
    )
    plt.bar(
        x + width / 2,
        df["frequency_lang"],
        width,
        label="Language"
    )

    plt.xticks(x, df["word"], rotation=45, ha="right")
    plt.title("Relative word frequency comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    print(f"Chart saved to {chart_path}")


def analyze_relative_word_frequency(mode, n, chart_path):
    article_counts = load_word_counts()

    if not article_counts:
        print("No word counts available. Run --count-words first.")
        return

    max_article_freq = max(article_counts.values())

    rows = []

    if mode == "article":
        sorted_article = sorted(article_counts.items(),key=lambda x: x[1],reverse=True)[:n]
        #TODO remove sorted from count-words

        for word, count in sorted_article:
            lang_freq = zipf_frequency(word, mode)
            rows.append({
                "word": word,
                "frequency_art": count / max_article_freq,
                "frequency_lang": lang_freq if lang_freq > 0 else None
            })

    elif mode == "language":
        top_language_words = top_n_list(mode, n)

        for word in top_language_words:
            article_freq = article_counts.get(word)
            rows.append({
                "word": word,
                "frequency_art": (
                    article_freq / max_article_freq if article_freq else None
                ),
                "frequency_lang": zipf_frequency(word, mode)
            })

    df = pd.DataFrame(rows)
    print(df)

    if chart_path:
        create_bar_chart(df, chart_path)


def get_links(soup):
    links = []
    for link in soup.find_all("a", href=True):
        if link["href"].startswith("/wiki/") and ":" not in link["href"]:
            links.append(link["href"])
    return links

def get_phrase(link):
    last_phrase = link.split("/")[-1]
    correct_phrase = last_phrase.replace("_", " ")
    return correct_phrase


def auto_count_words(phrase, depth, t):
    current_phrase = phrase
    links = []
    visited_links = set()

    while depth > 0:
        print(f"Depth: {depth}")
        print(current_phrase)

        content_div = get_article_div_soup(current_phrase)
        if depth > 1:
            current_links = get_links(content_div)
            print(f"Number of links for current phrase '{current_phrase}': {len(current_links)}")
            print("----------------")
            links.extend(current_links)

        count_words(current_phrase, content_div)

        if not links:
            break
        used_link = links.pop(0)
        if used_link in visited_links:
            continue

        visited_links.add(used_link)
        new_phrase = get_phrase(used_link)
        current_phrase = new_phrase
        depth -= 1
        time.sleep(t)


def main():
    scraper = WikiScraper()
    parser = Parser()
    args = parsing()

    what_task(args)
    #TODO artykul nie jest dostepny -> co wtedy?

if __name__ == "__main__":
    main()