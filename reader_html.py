import requests
from pathlib import Path


class ReaderHTML:
    def __init__(self, url: str,  use_local_html_file_instead=False):
        self.url = url
        self.use_local_html_file_instead = use_local_html_file_instead

    def _make_request(self, phrase: str):
        phrase_formatted = phrase.replace(" ", "_")
        try:
            response = requests.get(self.url + phrase_formatted)
            return response.text
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred while making the request: {req_err}")
            return None

    def _read_local(self, phrase: str):
        phrase_file_name = phrase.replace(" ", "_")
        path = Path(f"data/{phrase_file_name}.html")

        try:
            with path.open('r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: The file at {path} was not found.")
            return None

    def read_data(self, phrase: str = None) -> str:
        if self.use_local_html_file_instead and phrase is not None:
            return self._read_local(phrase)
        elif phrase is not None:
            return self._make_request(phrase)
        else:
            raise ValueError("Either phrase or file_path must be provided")
