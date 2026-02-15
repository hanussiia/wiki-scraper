from parser_html import ParserHTML
from table_generator import TableGenerator
from word_analyzer import WordAnalyzer


class Controller:
    def __init__(self, parser: ParserHTML, language: str='en',
                 args: dict=None):
        self.args = args
        self.parser = parser
        self.language = language
        self.table_generator = TableGenerator(parser)
        self.word_analyzer = WordAnalyzer(parser, language=self.language)

    def what_task(self):
        if self.args.summary:
            self.summary(self.args.summary)
        elif self.args.table:
            self.table(self.args.table,
                       self.args.number,
                       self.args.first_row_is_header)
        elif self.args.count_words:
            self.count_words(self.args.count_words)
        elif self.args.analyze_relative:
            self.analyze_relative(mode=self.args.mode,
                                  n=self.args.count,
                                  chart_path=self.args.chart)
        elif self.args.auto_count_words:
            self.auto_count_words(phrase=self.args.auto_count_words,
                                  depth=self.args.depth,
                                  t=self.args.wait)

    def summary(self, phrase: str):
        soup = self.parser.get_article(phrase)
        paragraph = soup.select_one('p').text.strip()
        print(paragraph)
        return paragraph

    def table(self, phrase: str, number: int, first_row_is_header: bool):
        table = self.table_generator.run(phrase, number, first_row_is_header)
        return table

    def count_words(self, phrase: str, prefix=None, postfix=None):
        soup = self.parser.get_article(phrase)
        self.word_analyzer.count_words(phrase, soup,
                                       prefix=prefix,
                                       postfix=postfix)

    def analyze_relative(self, mode, n, chart_path):
        self.word_analyzer.analyze_relative_word_frequency(
            mode=mode, n=n, chart_path=chart_path)

    def auto_count_words(self, phrase, depth, t):
        self.word_analyzer.auto_count_words(phrase, depth=depth, t=t)

    def load_word_counts(self, file_path):
        return self.word_analyzer.load_word_counts(file_path)
