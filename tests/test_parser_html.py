from parser_html import ParserHTML
from bs4 import BeautifulSoup


def test_get_text_removes_tags():
    html = """
    <div>
        Hello<br>World
        <script>bad()</script>
        <div id="column-one">remove</div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div")

    parser = ParserHTML("https://test.com/")
    text = parser.get_text(div)

    assert text == "Hello World"


def test_extract_words():
    parser = ParserHTML("https://test.com/")
    words = parser.extract_words("Hello world! It's 2025.")

    assert words == ["hello", "world", "it's"]

def test_get_links():
    html = """
    <div>
        <a href="/wiki/Valid_link">ok</a>
        <a href="/wiki/File:Something">skip</a>
        <a href="/other/page">skip</a>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    parser = ParserHTML("https://test.com/")
    links = parser.get_links(soup)

    assert links == ["/wiki/Valid_link"]


def test_get_phrase():
    parser = ParserHTML("https://test.com/")
    phrase = parser.get_phrase("/wiki/Hello_World")

    assert phrase == "Hello World"