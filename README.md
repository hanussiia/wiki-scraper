# Wiki-scraper
Narzędzie w języku Python służące do pobierania, analizy danych oraz wizualizacji statystyk słów. Podstawową wiki jest Bulbapedia.

## Funkcjonalności

Program obsługuje następujące polecenia uruchamiane z poziomu terminala:

* **Podsumowanie (`--summary`)**: Pobiera pierwszy paragraf artykułu dla podanej frazy, usuwając tagi HTML.
* **Przetwarzanie tabel (`--table`)**: Wyciąga $n$-tą tabelę ze strony, zapisuje ją do pliku `.csv` i generuje statystykę wystąpień wartości.
* **Licznik słów (`--count-words`)**: Zlicza słowa w artykule i aktualizuje zbiorczy plik JSON `word-counts.json`.
* **Analiza częstotliwości (`--analyze-relative-word-frequency`)**: Porównuje popularność słów na Wiki z ogólną częstotliwością w danym języku (opcjonalnie z wykresem słupkowym).
* **Automatyczny crawling (`--auto-count-words`)**: Rekurencyjnie odwiedza linki do określonej głębokości $n$, budując bazę słów z zachowaniem odstępów czasowych.

## Architektura i Testy

Program został zaprojektowany obiektowo, co pozwala na wykorzystanie jego modułów w skryptach lub notatnikach Jupyter.

* **Zgodność**: Kod napisany zgodnie ze standardem PEP8.
* **Unit Tests**: Zestaw 4 testów jednostkowych weryfikujących logikę bez połączenia z siecią.
* **Integration Test**: Skrypt `wiki_scraper_integration_test.py` sprawdzający pełny przepływ danych na plikach lokalnych.

## Analiza Języka (Jupyter Notebook)

W dołączonym notatniku znajduje się funkcja `lang_confidence_score`, która jest stworzona na podstawie jaccard similarity. Metoda ta pozwala na szybkie porównanie zbioru słów tekstu z listą $k$ najpopularniejszych wyrazów wzorcowych.

$$\text{J(A, B)} = \frac{|A \cap B|}{|A \cup B|}$$

1. **Przecięcie (Intersection)**: Liczba unikalnych słów, które występują jednocześnie w tekście i w liście top-K.
2. **Suma (Union)**: Całkowita liczba unikalnych słów występujących w obu zbiorach łącznie.
3. **Wynik**: Wartość z przedziału $[0, 1]$. Wynik **1** oznacza, że zbiory są identyczne, natomiast **0** oznacza całkowity brak wspólnych słów.

## Instalacja

1. Skonfiguruj środowisko wirtualne.
2. Zainstaluj wymagane biblioteki z requirements.txt `pip install -r requierements.txt`.
3. Uruchom test integracyjny: `python3 wiki_scraper_integration_test.py` i testy jednostkowe z folderu wiki-scraoer `pytest`.