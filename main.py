"""Ponto de entrada do projeto de análise exploratória de URLs."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.pipeline import FIGURES_DIR, run_pipeline


def create_charts(data: pd.DataFrame) -> None:
    """Gera gráficos exploratórios e os salva na pasta de relatórios."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Gráfico 1: quantidade de registros em cada classe.
    class_counts = data["label"].value_counts().reindex(
        ["legitima", "phishing"], fill_value=0
    )
    ax = class_counts.plot(kind="bar", rot=0, figsize=(8, 5))
    ax.set_title("Quantidade de registros por classificação")
    ax.set_xlabel("Classificação")
    ax.set_ylabel("Quantidade de URLs")
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "distribuicao_classes.png", dpi=150)
    plt.close()

    # Gráfico 2: compara a distribuição do comprimento textual das URLs.
    fig, ax = plt.subplots(figsize=(8, 5))
    data.boxplot(column="url_length", by="label", ax=ax, grid=False)
    fig.suptitle("")
    ax.set_title("Comprimento das URLs por classificação")
    ax.set_xlabel("Classificação")
    ax.set_ylabel("Quantidade de caracteres")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "comprimento_urls.png", dpi=150)
    plt.close()

    # Gráfico 3: compara a frequência de alguns indicadores estruturais.
    feature_columns = [
        "has_https",
        "has_ip_address",
        "has_at_symbol",
        "has_suspicious_keyword",
    ]
    rates = data.groupby("label")[feature_columns].mean().T
    ax = rates.plot(kind="bar", figsize=(10, 5))
    ax.set_title("Proporção de registros com cada indicador")
    ax.set_xlabel("Indicador")
    ax.set_ylabel("Proporção")
    ax.set_ylim(0, 1)
    ax.legend(title="Classificação")
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "indicadores_estruturais.png", dpi=150)
    plt.close()


def main() -> None:
    """Coordena o processamento, a geração dos gráficos e o resumo final."""
    data, summary = run_pipeline()
    create_charts(data)

    print("\nANÁLISE CONCLUÍDA")
    print(f"Registros válidos analisados: {len(data)}")
    print("\nResumo estatístico por classe:")
    print(summary.to_string(index=False))
    print("\nArquivos gerados em: data/processed/ e reports/")


if __name__ == "__main__":
    main()
