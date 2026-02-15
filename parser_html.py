from bs4 import BeautifulSoup
import re
from reader_html import ReaderHTML


class ParserHTML:
    def __init__(self, url: str, use_local_html_file_instead: bool=False):
        self.reader = ReaderHTML(url, use_local_html_file_instead)

    def get_article(self, phrase):
        soup = self._get_soup(phrase)
        if soup is None:
            return None
        return soup
    
    def get_table_soup(self, phrase):
        soup = self._get_soup(phrase)
        if soup is None:
            return []
        return soup.find_all('table')
    
    def get_text(self, content_div):
        if content_div is None:
            return ""

        for br in content_div.find_all("br"):
            br.replace_with(" ")
        
        for tag in content_div.find_all([
            "header", "nav", "footer", "aside", "style", "script"
        ]):
            tag.decompose()

        column_one = content_div.find("div", id="column-one")
        if column_one:
            column_one.decompose()

        text = content_div.get_text(separator=" ")
        return " ".join(text.split())

    def extract_words(self, text: str):
        return re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text.lower(), flags=re.UNICODE)


    def get_links(self, soup):
        links = []
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("/wiki/") and ":" not in link["href"]:
                links.append(link["href"])
        return links
    
    def get_phrase(self, link):
        last_phrase = link.split("/")[-1]
        correct_phrase = last_phrase.replace("_", " ")
        return correct_phrase
    

    def _get_soup(self, phrase) -> BeautifulSoup:
        data = self.reader.read_data(phrase)
        if data is None:
            print(f"The page for phrase '{phrase}' could not be retrieved.")
            return None
        return BeautifulSoup(data, "html.parser") 