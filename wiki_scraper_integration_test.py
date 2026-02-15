
from parser_html import ParserHTML
from controller import Controller
import pandas as pd
import os 
def main():

    controller = Controller(ParserHTML(url="", use_local_html_file_instead=True))
    summary = controller.summary("Team Rocket")

    assert summary.startswith("Team Rocket")
    assert summary.endswith("Sevii Islands.")

    controller.count_words("Team Rocket", "team_rocket", "en")

    assert os.path.exists("team_rocket-en-word-counts.json")
    

if __name__ == "__main__":
    main()