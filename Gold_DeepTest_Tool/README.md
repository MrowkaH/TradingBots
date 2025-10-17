# OBGold DeepTest

Zestaw narzędzi do „głębokiego” testowania strategii tradingowej wyłącznie na złocie (Gold / XAU, GC=F). Pozwala szybko podpiąć własną zależność/zasadę, uruchomić backtest, grid search, walk‑forward, test permutacyjny (p‑value) oraz bootstrapowe przedziały ufności.

## Co jest w środku

Struktura w `OBGold/deeptest/`:
- `data_loader.py` – ładowanie danych (Yahoo Finance: GC=F/XAUUSD, CSV, fallback syntetyczny) i wyliczenie zwrotów.
- `strategy_template.py` – prosty kontrakt strategii + przykładowa MA cross; podmień na własną zależność.
- `backtester.py` – wektorowy backtest (pozycja, koszty, krzywa kapitału).
- `metrics.py` – metryki: CAGR, Sharpe, Sortino, MaxDD, Calmar, itp.
- `deep_test.py` – grid search, walk‑forward, permutation test, bootstrap CI.
- `run_example.py` – przykład uruchomienia end‑to‑end.

## Wymagania

Python 3.10+ oraz pakiety:
- pandas
- numpy
- yfinance (opcjonalnie; jeśli brak – użyty zostanie syntetyczny szereg)

Możesz zainstalować je w swoim środowisku:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
#potem
pip install -r OBGold/requirements.txt
```

## Szybki start
```powershell 
python -m OBGold.deeptest.run_example
```

Skrypt:
1) Ładuje dane (GC=F od 2015).
2) Uruchamia grid search dla prostego MA cross.
3) Wykonuje walk‑forward (3y train / 1y test).
4) Liczy p‑value testem permutacyjnym (CAGR vs. reshuffle w blokach).
5) Liczy bootstrapowe CI dla CAGR.

## Jak podpiąć własną zależność (strategię)

1. Otwórz `strategy_template.py` i dodaj funkcję zgodną z kontraktem:
   - Wejście: `df: pd.DataFrame` z kolumnami co najmniej `Close` i `RetSimple`.
   - Parametry: `params: Dict[str, Any]`.
   - Wyjście: `pd.Series` z pozycją docelową w przedziale [-1..1] (np. -1 short, 0 flat, 1 long), indeks zgodny z `df.index`.
2. Dodaj ją do słownika `BUILT_IN_STRATEGIES` lub zaimportuj w swoim skrypcie i przekaż bezpośrednio do funkcji z `deep_test.py`.
3. Zdefiniuj siatkę parametrów (grid) pod swój pomysł i użyj:
   - `grid_search(df, strategia, grid, cost)`
   - `walk_forward(df, strategia, grid, cost, WalkForwardConfig(...))`
   - `permutation_test(df, strategia, params, cost, n_iter=..., block=...)`
   - `bootstrap_ci(df, strategia, params, cost, n_iter=..., block=...)`

## Uwagi praktyczne

- Dane: `GC=F` (futures) i `XAUUSD=X` (spot) w Yahoo różnią się; wybierz właściwy symbol w `DataConfig`.
- Koszty: ustaw realistyczne bpsy w `CostModel` (commission + slippage). Wyniki są czułe na koszty.
- Walk‑forward: krótsze okna dadzą szybszą adaptację, ale mogą zwiększyć wariancję.
- Test permutacyjny i bootstrap: zwiększ `n_iter` dla lepszej stabilności (kosztem czasu).

## Co dalej

- Dodanie testów jednostkowych i wykresów (equity, heatmapy gridu) – do rozważenia.
- Integracja z Twoim silnikiem egzekucji, jeśli strategia przejdzie rygor testów.

