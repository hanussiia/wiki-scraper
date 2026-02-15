from wordfreq import top_n_list, zipf_frequency
import pandas as pd
import matplotlib.pyplot as plt 
from parser_html import ParserHTML
import time 
import numpy as np 
import json
from pathlib import Path 

class WordAnalyzer: 

    def __init__(self, parser:ParserHTML, language="en"):
        self.parser = parser
        self.language = language


    def count_words(self, phrase:str, soup, prefix=None, postfix=None):
        article_text = self.parser.get_text(soup)
        if not article_text:
            print("No article text found")
            return

        words = self.parser.extract_words(article_text)

        global_counts = self.load_word_counts(prefix=prefix, postfix=postfix)
        global_counts = self.update_word_counts(global_counts, words)
      
        self.save_word_counts(global_counts, prefix=prefix, postfix=postfix)
        print(f"Counted {len(set(words))} unique words from article '{phrase}'")


    def analyze_relative_word_frequency(self, mode, n, chart_path):
        article_counts = self.load_word_counts(prefix=None, postfix=None)

        if not article_counts:
            print("No word counts available. Run --count-words first.")
            return

        max_article_freq = max(article_counts.values())

        rows = []

        if mode == "article":
            sorted_article = sorted(article_counts.items(),key=lambda x: x[1],reverse=True)[:n]

            for word, count in sorted_article:
                lang_freq = zipf_frequency(word, self.language) / 8
                rows.append({
                    "word": word,
                    "frequency_art": count / max_article_freq,
                    "frequency_lang": lang_freq if lang_freq > 0 else None
                })

        elif mode == "language":
            top_language_words = top_n_list(self.language, n)

            for word in top_language_words:
                article_freq = article_counts.get(word)
                rows.append({
                    "word": word,
                    "frequency_art": (
                        article_freq / max_article_freq if article_freq else None
                    ),
                    "frequency_lang": zipf_frequency(word, self.language) / 8
                })

        df = pd.DataFrame(rows)
        print(df)

        if chart_path:
            self.create_bar_chart(df, chart_path)


    def auto_count_words(self, phrase:str, depth:int, t:int):
        current_phrase = phrase
        links = []
        visited_links = set()

        while depth > 0:
            print(f"Depth: {depth}")
            print(current_phrase)

            content_div = self.parser.get_article_div_soup(current_phrase)
            if content_div is None:
                print(f"Could not retrieve content for phrase '{current_phrase}'")
                return None
            
            if depth > 1:
                current_links = self.parser.get_links(content_div)
                print(f"Number of links for current phrase '{current_phrase}': {len(current_links)}")
                print("----------------")
                links.extend(current_links)

            self.count_words(current_phrase, content_div)

            if not links:
                break
            used_link = links.pop(0)
            if used_link in visited_links:
                continue

            visited_links.add(used_link)
            new_phrase = self.parser.get_phrase(used_link)
            current_phrase = new_phrase
            depth -= 1
            time.sleep(t)


    def load_word_counts(self, path=None, prefix=None, postfix=None):
        if prefix and postfix:
            path = f"{prefix}-{postfix}-word-counts.json"
        else:
            path = "word-counts.json"

        if not Path(path).exists():
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


    def save_word_counts(self, counts:int, prefix: str=None, postfix:str=None):
        if postfix and prefix:
            path = f"{prefix}-{postfix}-word-counts.json"
        else:
            path = "word-counts.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(counts, f, indent=2, ensure_ascii=False)


    def update_word_counts(self, global_counts, words):
        for word in words:
            if word in global_counts:
                global_counts[word] += 1
            else:
                global_counts[word] = 1

        return global_counts
    

    def create_bar_chart(self, df, chart_path):
        df.set_index("word")[["frequency_art", "frequency_lang"]].plot(
            kind="bar",
            figsize=(12, 6)
        )
        plt.tight_layout()
        plt.savefig(chart_path)
        print(f"Chart saved to {chart_path}")
