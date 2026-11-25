"""Leitura, validação, análise e exportação dos dados do projeto."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.features import FEATURE_COLUMNS, add_url_features

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT_DIR / "data" / "raw" / "urls_exemplo.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
DATABASE_FILE = PROCESSED_DIR / "analise_urls.db"

VALID_LABELS = {"legitima", "phishing"}


def load_and_validate_data(file_path: str | Path = RAW_FILE) -> pd.DataFrame:
    """Carrega o CSV, valida campos e rejeita rótulos conflitantes."""
    source = Path(file_path)
    if not source.is_file():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {source}")

    try:
        data = pd.read_csv(
            source,
            dtype={"url": "string", "label": "string"},
            keep_default_na=False,
        )
    except pd.errors.EmptyDataError as error:
        raise ValueError("O arquivo CSV está vazio ou não contém cabeçalho.") from error

    required_columns = {"url", "label"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    data = data[["url", "label"]].copy()
    data["url"] = data["url"].str.strip()
    data["label"] = data["label"].str.strip().str.lower()
    data = data.loc[
        data["url"].ne("") & data["label"].isin(VALID_LABELS)
    ].copy()

    if data.empty:
        raise ValueError(
            "Não há registros válidos. Verifique URLs e rótulos "
            "('legitima' ou 'phishing')."
        )

    # Uma mesma URL com rótulos diferentes indica conflito na fonte dos dados.
    conflicting_urls = data.groupby("url")["label"].nunique()
    conflicting_urls = conflicting_urls[conflicting_urls > 1]
    if not conflicting_urls.empty:
        raise ValueError(
            f"Foram encontradas {len(conflicting_urls)} URL(s) com rótulos "
            "conflitantes. Corrija a classificação antes da análise."
        )

    return data.drop_duplicates(subset=["url", "label"]).reset_index(drop=True)


def build_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula contagem, média e mediana dos indicadores por classe."""
    missing_columns = set(FEATURE_COLUMNS).difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas de características ausentes: {missing}")
    if "label" not in data.columns:
        raise ValueError("A coluna obrigatória 'label' não foi encontrada.")
    if data.empty:
        raise ValueError("Não há registros para gerar o resumo estatístico.")

    summary = data.groupby("label")[list(FEATURE_COLUMNS)].agg(
        ["count", "mean", "median"]
    )
    summary.columns = [f"{column}_{stat}" for column, stat in summary.columns]
    return summary.reset_index().replace([np.inf, -np.inf], np.nan)


def save_database(
    data: pd.DataFrame,
    database_file: str | Path = DATABASE_FILE,
) -> None:
    """Cria ou substitui a tabela analítica em um banco SQLite local."""
    destination = Path(database_file)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(destination) as connection:
        data.to_sql("urls_analysis", connection, if_exists="replace", index=False)


def run_pipeline(
    input_file: str | Path = RAW_FILE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa o pipeline e exporta CSV, resumo e banco SQLite."""
    raw_data = load_and_validate_data(input_file)
    enriched_data = add_url_features(raw_data)
    summary = build_summary(enriched_data)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    enriched_data.to_csv(
        PROCESSED_DIR / "urls_analisadas.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary.to_csv(
        REPORTS_DIR / "resumo_por_classe.csv",
        index=False,
        encoding="utf-8-sig",
    )
    save_database(enriched_data)

    return enriched_data, summary
