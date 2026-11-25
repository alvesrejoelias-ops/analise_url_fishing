"""Ponto de entrada da análise exploratória de URLs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.pipeline import FIGURES_DIR, RAW_FILE, run_pipeline


def create_charts(data: pd.DataFrame) -> None:
    """Gera gráficos exploratórios e os salva na pasta de relatórios."""
    required_columns = {
        "label",
        "url_length",
        "has_https",
        "has_ip_address",
        "has_at_symbol",
        "has_suspicious_keyword",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas necessárias para os gráficos ausentes: {missing}")
    if data.empty:
        raise ValueError("Não há dados para gerar gráficos.")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    class_counts = data["label"].value_counts().reindex(
        ["legitima", "phishing"], fill_value=0
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    class_counts.plot(kind="bar", rot=0, ax=ax)
    ax.set_title("Quantidade de registros por classificação")
    ax.set_xlabel("Classificação")
    ax.set_ylabel("Quantidade de URLs")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "distribuicao_classes.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    data.boxplot(column="url_length", by="label", ax=ax, grid=False)
    fig.suptitle("")
    ax.set_title("Comprimento das URLs por classificação")
    ax.set_xlabel("Classificação")
    ax.set_ylabel("Quantidade de caracteres")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "comprimento_urls.png", dpi=150)
    plt.close(fig)

    feature_columns = [
        "has_https",
        "has_ip_address",
        "has_at_symbol",
        "has_suspicious_keyword",
    ]
    rates = data.groupby("label")[feature_columns].mean().T
    fig, ax = plt.subplots(figsize=(10, 5))
    rates.plot(kind="bar", ax=ax)
    ax.set_title("Proporção de registros com cada indicador")
    ax.set_xlabel("Indicador")
    ax.set_ylabel("Proporção")
    ax.set_ylim(0, 1)
    ax.legend(title="Classificação")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", labelrotation=15)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "indicadores_estruturais.png", dpi=150)
    plt.close(fig)


def main() -> None:
    """Executa o pipeline, gera os gráficos e exibe o resumo."""
    parser = argparse.ArgumentParser(
        description="Analisa características estruturais de URLs em um CSV."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=RAW_FILE,
        help="Caminho do CSV de entrada (padrão: data/raw/urls_exemplo.csv).",
    )
    args = parser.parse_args()

    data, summary = run_pipeline(args.input)
    create_charts(data)

    print("\nANÁLISE CONCLUÍDA")
    print(f"Registros válidos analisados: {len(data)}")
    print("\nResumo estatístico por classe:")
    print(summary.to_string(index=False))
    print("\nArquivos gerados em: data/processed/ e reports/")


if __name__ == "__main__":
    main()
