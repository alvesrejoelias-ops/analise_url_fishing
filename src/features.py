"""Extração de características estruturais de URLs.

Este módulo trata cada URL somente como texto. Nenhuma conexão de rede é realizada.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

import pandas as pd

# Termos selecionados para uma triagem exploratória.
# A presença de uma palavra não comprova intenção fraudulenta.
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


def _parse_url(url: str):
    """Interpreta uma URL sem acessá-la, adicionando esquema quando necessário."""
    value = str(url).strip()
    candidate = value if "://" in value else f"//{value}"
    return urlsplit(candidate)


def _host_is_ip(host: str) -> int:
    """Retorna 1 quando o nome do host representa um endereço IP válido."""
    if not host:
        return 0

    try:
        ipaddress.ip_address(host.strip("[]"))
        return 1
    except ValueError:
        return 0


def extract_url_features(url: str) -> dict:
    """Extrai métricas simples da estrutura textual de uma URL."""
    value = str(url).strip()
    parsed = _parse_url(value)
    host = parsed.hostname or ""
    host_parts = [part for part in host.split(".") if part]

    # Remove o prefixo www. da contagem aproximada de subdomínios.
    if host_parts and host_parts[0].lower() == "www":
        host_parts = host_parts[1:]

    lowered = value.lower()
    return {
        "url_length": len(value),
        "dot_count": value.count("."),
        "hyphen_count": value.count("-"),
        "digit_count": sum(character.isdigit() for character in value),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_ip_address": _host_is_ip(host),
        "has_at_symbol": int("@" in value),
        "subdomain_count": max(len(host_parts) - 2, 0),
        "query_parameter_count": len(
            [part for part in parsed.query.split("&") if part]
        ),
        "has_suspicious_keyword": int(
            any(keyword in lowered for keyword in SUSPICIOUS_KEYWORDS)
        ),
    }


def add_url_features(data: pd.DataFrame) -> pd.DataFrame:
    """Adiciona as características calculadas a uma cópia da base recebida."""
    features = data["url"].apply(extract_url_features).apply(pd.Series)
    return pd.concat([data.copy(), features], axis=1)
