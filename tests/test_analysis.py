"""Testes automatizados das funções de análise e validação."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.features import add_url_features, extract_url_features
from src.pipeline import build_summary, load_and_validate_data, save_database


class TestUrlFeatures(unittest.TestCase):
    def test_https_and_query_parameters(self):
        result = extract_url_features("https://example.com/search?q=data&page=2")
        self.assertEqual(result["has_https"], 1)
        self.assertEqual(result["query_parameter_count"], 2)
        self.assertEqual(result["has_ip_address"], 0)

    def test_ipv4_and_ipv6_are_detected(self):
        ipv4 = extract_url_features("http://192.0.2.10/login")
        ipv6 = extract_url_features("https://[2001:db8::1]/")
        self.assertEqual(ipv4["has_ip_address"], 1)
        self.assertEqual(ipv6["has_ip_address"], 1)
        self.assertEqual(ipv4["subdomain_count"], 0)
        self.assertEqual(ipv6["subdomain_count"], 0)

    def test_malformed_url_does_not_raise(self):
        result = extract_url_features("https://[endereco-invalido")
        self.assertEqual(result["has_ip_address"], 0)
        self.assertEqual(result["url_length"], len("https://[endereco-invalido"))

    def test_at_symbol_is_only_counted_in_authority(self):
        in_authority = extract_url_features("https://user@example.com/path")
        in_query = extract_url_features("https://example.com/path?email=a@b.com")
        self.assertEqual(in_authority["has_at_symbol"], 1)
        self.assertEqual(in_query["has_at_symbol"], 0)

    def test_subdomain_count_ignores_www_and_trailing_dot(self):
        result = extract_url_features("https://www.shop.store.example.com./")
        self.assertEqual(result["subdomain_count"], 2)

    def test_keyword_is_only_a_structural_flag(self):
        result = extract_url_features("https://example.com/account")
        self.assertEqual(result["has_suspicious_keyword"], 1)
        self.assertNotIn("prediction", result)

    def test_none_is_handled_as_empty_text(self):
        result = extract_url_features(None)
        self.assertEqual(result["url_length"], 0)
        self.assertEqual(result["has_https"], 0)

    def test_features_do_not_change_input_or_duplicate_columns(self):
        original = pd.DataFrame(
            {"url": ["https://example.com"], "label": ["legitima"]}
        )
        enriched = add_url_features(original)
        enriched_again = add_url_features(enriched)
        self.assertEqual(list(original.columns), ["url", "label"])
        self.assertEqual(enriched_again.columns.tolist().count("url_length"), 1)

    def test_missing_url_column_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, "coluna obrigatória 'url'"):
            add_url_features(pd.DataFrame({"label": ["legitima"]}))


class TestDataValidation(unittest.TestCase):
    def test_loads_csv_and_removes_invalid_rows_and_duplicates(self):
        content = (
            "url,label\n"
            "https://example.com,legitima\n"
            "https://example.com,legitima\n"
            ",phishing\n"
            "https://bad.example,unknown\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "input.csv"
            csv_path.write_text(content, encoding="utf-8")
            data = load_and_validate_data(str(csv_path))

        self.assertEqual(len(data), 1)
        self.assertEqual(data.iloc[0]["label"], "legitima")

    def test_missing_columns_raise_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "input.csv"
            csv_path.write_text("url\nhttps://example.com\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Colunas obrigatórias ausentes"):
                load_and_validate_data(csv_path)

    def test_conflicting_labels_raise_clear_error(self):
        content = (
            "url,label\n"
            "https://example.com,legitima\n"
            "https://example.com,phishing\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "input.csv"
            csv_path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rótulos conflitantes"):
                load_and_validate_data(csv_path)

    def test_empty_csv_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "input.csv"
            csv_path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CSV está vazio"):
                load_and_validate_data(csv_path)


class TestAnalysisOutputs(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "label": ["legitima", "legitima", "phishing"],
                "url_length": [20, 30, 45],
                "dot_count": [1, 1, 2],
                "hyphen_count": [0, 0, 2],
                "digit_count": [0, 0, 3],
                "has_https": [1, 1, 0],
                "has_ip_address": [0, 0, 1],
                "has_at_symbol": [0, 0, 0],
                "subdomain_count": [0, 1, 0],
                "query_parameter_count": [0, 1, 2],
                "has_suspicious_keyword": [0, 0, 1],
            }
        )

    def test_summary_has_one_row_per_label(self):
        summary = build_summary(self.data)
        self.assertEqual(set(summary["label"]), {"legitima", "phishing"})
        self.assertIn("url_length_mean", summary.columns)
        self.assertIn("url_length_median", summary.columns)

    def test_summary_rejects_missing_feature_columns(self):
        with self.assertRaisesRegex(ValueError, "características ausentes"):
            build_summary(pd.DataFrame({"label": ["legitima"]}))

    def test_sqlite_database_is_created_with_expected_table(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "output" / "analysis.db"
            save_database(self.data, database_path)
            with sqlite3.connect(database_path) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM urls_analysis"
                ).fetchone()[0]
        self.assertEqual(count, len(self.data))


if __name__ == "__main__":
    unittest.main()
