"""Leitura, validação, análise e exportação dos dados do projeto."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.features import add_url_features

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT_DIR / "data" / "raw" / "urls_exemplo.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
DATABASE_FILE = PROCESSED_DIR / "analise_urls.db"

VALID_LABELS = {"legitima", "phishing"}


def load_and_validate_data(file_path: Path = RAW_FILE) -> pd.DataFrame:
    """Carrega o CSV e verifica os campos essenciais antes da análise."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {file_path}. "
            "Verifique a pasta data/raw."
        )

    data = pd.read_csv(file_path)

    required_columns = {"url", "label"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {', '.join(sorted(missing_columns))}"
        )

    data = data[["url", "label"]].copy()
    data["url"] = data["url"].fillna("").astype(str).str.strip()
    data["label"] = data["label"].fillna("").astype(str).str.strip().str.lower()

    # Registros sem URL ou sem uma classificação válida não entram na análise.
    data = data[(data["url"] != "") & (data["label"].isin(VALID_LABELS))]
    data = data.drop_duplicates(subset=["url", "label"]).reset_index(drop=True)

    if data.empty:
        raise ValueError("Não há registros válidos após a etapa de validação.")

    return data


def build_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula estatísticas descritivas por classe."""
    numeric_columns = [
        "url_length",
        "dot_count",
        "hyphen_count",
        "digit_count",
        "has_https",
        "has_ip_address",
        "has_at_symbol",
        "subdomain_count",
        "query_parameter_count",
        "has_suspicious_keyword",
    ]

    summary = data.groupby("label")[numeric_columns].agg(["count", "mean", "median"])
    summary.columns = [f"{column}_{stat}" for column, stat in summary.columns]
    summary = summary.reset_index()

    # Garante que valores numéricos ausentes não contaminem os cálculos.
    summary = summary.replace([np.inf, -np.inf], np.nan)
    return summary


def save_database(data: pd.DataFrame) -> None:
    """Cria ou substitui a tabela analítica no banco SQLite local."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_FILE) as connection:
        data.to_sql("urls_analysis", connection, if_exists="replace", index=False)


def run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa todas as etapas e salva os resultados em arquivos locais."""
    raw_data = load_and_validate_data()
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
