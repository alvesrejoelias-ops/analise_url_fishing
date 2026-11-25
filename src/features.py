"""Extrai características estruturais de URLs sem acessá-las."""

from __future__ import annotations

import ipaddress
from urllib.parse import SplitResult, parse_qsl, urlsplit

import pandas as pd

# Termos para uma triagem exploratória. Sua presença não comprova fraude.
SUSPICIOUS_KEYWORDS = (
    "login",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "password",
    "confirm",
    "authentication",
    "billing",
)

FEATURE_COLUMNS = (
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
)


def _parse_url(value: str) -> SplitResult:
    """Interpreta a URL sem rede e tolera entradas com sintaxe inválida."""
    candidate = value if "://" in value else f"//{value}"
    try:
        return urlsplit(candidate)
    except ValueError:
        # Entradas malformadas continuam sendo analisadas como texto; não podem
        # interromper todo o processamento do arquivo.
        return urlsplit("")


def _host_is_ip(host: str) -> int:
    """Retorna 1 quando o host é um endereço IPv4 ou IPv6 válido."""
    if not host:
        return 0

    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return 0
    return 1


def extract_url_features(url: str | None) -> dict[str, int]:
    """Calcula indicadores simples a partir do texto de uma URL."""
    value = "" if url is None else str(url).strip()
    parsed = _parse_url(value)

    try:
        host = parsed.hostname or ""
    except ValueError:
        host = ""

    is_ip_address = _host_is_ip(host)
    normalized_host = host.rstrip(".")
    host_parts = [part for part in normalized_host.split(".") if part]

    # A contagem é aproximada e não se aplica a endereços IP.
    if is_ip_address:
        subdomain_count = 0
    else:
        if host_parts and host_parts[0].lower() == "www":
            host_parts = host_parts[1:]
        subdomain_count = max(len(host_parts) - 2, 0)

    lowered = value.lower()
    query_parameters = parse_qsl(parsed.query, keep_blank_values=True)

    return {
        "url_length": len(value),
        "dot_count": value.count("."),
        "hyphen_count": value.count("-"),
        "digit_count": sum(character.isdigit() for character in value),
        "has_https": int(value.lower().startswith("https://")),
        "has_ip_address": is_ip_address,
        # O @ só é considerado quando aparece na autoridade (userinfo/host).
        "has_at_symbol": int("@" in parsed.netloc),
        "subdomain_count": subdomain_count,
        "query_parameter_count": len(query_parameters),
        "has_suspicious_keyword": int(
            any(keyword in lowered for keyword in SUSPICIOUS_KEYWORDS)
        ),
    }


def add_url_features(data: pd.DataFrame) -> pd.DataFrame:
    """Adiciona as características em uma cópia, sem duplicar colunas."""
    if "url" not in data.columns:
        raise ValueError("A coluna obrigatória 'url' não foi encontrada.")

    base = data.drop(columns=list(FEATURE_COLUMNS), errors="ignore").copy()
    if base.empty:
        for column in FEATURE_COLUMNS:
            base[column] = pd.Series(index=base.index, dtype="int64")
        return base

    records = base["url"].map(extract_url_features).tolist()
    features = pd.DataFrame.from_records(records, index=base.index)
    return base.join(features)
