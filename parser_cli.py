import argparse


class ParserCLI:
    def __init__(self):
        self.args = None
        self.parser = argparse.ArgumentParser()

    def _validation(self):
        # --- TABLE ---
        if self.args.table:
            if self.args.number is None:
                self.parser.error("--table requires --number")
            if self.args.number <= 0:
                self.parser.error("--number must be > 0")

        # --- ANALYSIS ---
        if self.args.analyze_relative:
            if not self.args.mode or not self.args.count:
                self.parser.error(
                    "--analyze-relative requires "
                    "--mode and --count"
                )
            if self.args.count <= 0:
                self.parser.error("--count must be > 0")

        # --- AUTO COUNT WORDS ---
        if self.args.auto_count_words:
            if self.args.depth <= 0 or self.args.wait <= 0:
                self.parser.error("--depth and --wait must be > 0")

        # --- TEXT LENGTH ---
        modes = [
            self.args.summary, self.args.table, self.args.count_words,
            self.args.analyze_relative, self.args.auto_count_words
        ]
        for arg in modes:
            if arg and len(arg) > 20:
                self.parser.error("article name must be <= 20 characters")

    def parsing(self):
        mode = self.parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--summary", type=str, nargs="?", const="Team Rocket",
            help="summarize wiki phrase, length <= 20",
            dest="summary"
        )
        mode.add_argument(
            "--table", type=str, nargs="?", const="Type",
            help="get table from wiki, length <= 20",
            dest="table"
        )
        mode.add_argument(
            "--count-words", type=str, nargs="?", const="Team Rocket",
            help="count words from wiki, length <= 20",
            dest="count_words"
        )
        mode.add_argument(
            "--analyze-relative", type=str, nargs="?", const="Team Rocket",
            help="compare frequency, length <= 20",
            dest="analyze_relative"
        )
        mode.add_argument(
            "--auto-count-words", type=str, nargs="?", const="Team Rocket",
            help="count words from wiki and links, length <= 20",
            dest="auto_count_words"
        )

        self.parser.add_argument(
            "--number", type=int,
            help="table number (--table)"
        )
        self.parser.add_argument(
            "--first-row-is-header", action="store_true",
            help="treat first row as header (--table)"
        )
        self.parser.add_argument(
            "--mode", type=str, choices=["article", "language"],
            default="article",
            help="mode: article or language (--analyze-relative)"
        )
        self.parser.add_argument(
            "--count", type=int, default=10,
            help="number of words to analyze (--analyze-relative)"
        )
        self.parser.add_argument(
            "--chart", type=str, default=".",
            help="path to save chart image (--analyze-relative)"
        )
        self.parser.add_argument(
            "--depth", type=int, default=2,
            help="depth of search (default=2) (--auto-count-words)"
        )
        self.parser.add_argument(
            "--wait", type=int, default=1,
            help="waiting time (default=1) (--auto-count-words)"
        )

        self.args = self.parser.parse_args()
        self._validation()
        return self.args
