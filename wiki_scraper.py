from controller import Controller
from parser_cli import ParserCLI
from parser_html import ParserHTML

def main():
    parser = ParserCLI()
    parser.parsing()
    url = "https://bulbapedia.bulbagarden.net/wiki/"

    controller = Controller(ParserHTML(url, use_local_html_file_instead=False), args=parser.args)
    controller.what_task()
    

if __name__ == "__main__":
    main()