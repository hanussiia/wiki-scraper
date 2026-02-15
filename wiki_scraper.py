from controller import Controller
from parser_cli import ParserCLI
from parser_html import ParserHTML

def main():
    parser = ParserCLI()
    parser.parsing()
    url = "https://bulbapedia.bulbagarden.net/wiki/"

    controller = Controller(ParserHTML(url), args=parser.args)
    controller.what_task()
    

if __name__ == "__main__":
    main()