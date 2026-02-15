import pandas as pd
from parser_html import ParserHTML


class TableGenerator:
    def __init__(self, parser: ParserHTML):
        self.parser = parser

    def run(self, phrase: str, number: int, first_row_is_header: bool):
        tables = self.parser.get_table_soup(phrase)
        if not tables:
            print("No tables found")
            return

        if number > len(tables):
            print("""Table number out of range,
            "so the last possible table is used""")
            number = len(tables)

        table_to_use = tables[number - 1]
        rows = table_to_use.find_all('tr')
        data = []

        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                data.append(row_data)
        print(data)
        df = pd.DataFrame(data)
        print(df)
        df = df.dropna(thresh=len(df)*0.9, axis=1)
        df = df.dropna(thresh=len(df.columns)*0.9, axis=0)

        df_without_header = df.drop(df.index[0]).reset_index(drop=True)
        if first_row_is_header:
            df.columns = df.iloc[0]
            print(df.columns)
            df = df_without_header

        if df is not None:
            print(df)

        # --- zapis do pliku ---
        filename = phrase.replace(" ", "_") + ".csv"
        df.to_csv(filename, index=False)
        print(f"Table saved to {filename}")

        df_counted_words = self._count_words_table(df_without_header)
        print(df_counted_words)
        return df_counted_words

    def _count_words_table(self, df: pd.DataFrame):
        counted_df = df.stack().value_counts().reset_index()
        counted_df.columns = ["value", "count"]
