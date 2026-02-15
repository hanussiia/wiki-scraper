from parser_html import ParserHTML
from table_generator import TableGenerator
from word_analyzer import WordAnalyzer


class Controller:
    def __init__(self, args:dict, parser:ParserHTML):
        self.args = args
        self.parser = parser
        self.table_generator = TableGenerator(parser)
        self.word_analyzer = WordAnalyzer(parser)


    def what_task(self):
        if self.args.summary:
            self._summary(self.args.summary)
        elif self.args.table:
            self.table_generator.run(self.args.table, self.args.number, self.args.first_row_is_header)
        elif self.args.count_words:
            soup = self.parser.get_article_div_soup(self.args.count_words)
            self.word_analyzer.count_words(self.args.count_words, soup)
        elif self.args.analyze_relative:
            self.word_analyzer.analyze_relative_word_frequency(mode=self.args.mode, n=self.args.count, chart_path=self.args.chart)
        elif self.args.auto_count_words:
            self.word_analyzer.auto_count_words(self.args.auto_count_words, depth=self.args.depth, t=self.args.wait)


    def _summary(self, phrase):
        soup = self.parser.get_article_div_soup(phrase)
        paragraph = soup.select_one('p').text.strip()
        print(paragraph)