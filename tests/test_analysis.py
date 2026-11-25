"""Testes automatizados básicos das funções de análise."""

import unittest

import pandas as pd

from src.features import add_url_features, extract_url_features
from src.pipeline import build_summary, load_and_validate_data


class TestUrlFeatures(unittest.TestCase):
    def test_https_and_query_parameters(self):
        result = extract_url_features("https://example.com/search?q=data&page=2")
        self.assertEqual(result["has_https"], 1)
        self.assertEqual(result["query_parameter_count"], 2)
        self.assertEqual(result["has_ip_address"], 0)

    def test_ip_address_is_detected(self):
        result = extract_url_features("http://192.0.2.10/login")
        self.assertEqual(result["has_ip_address"], 1)

    def test_keyword_is_only_a_structural_flag(self):
        result = extract_url_features("https://example.com/account")
        self.assertEqual(result["has_suspicious_keyword"], 1)
        # A palavra é um indicador textual, não uma classificação automática.
        self.assertNotIn("prediction", result)

    def test_features_do_not_change_input_dataframe(self):
        original = pd.DataFrame(
            {"url": ["https://example.com"], "label": ["legitima"]}
        )
        enriched = add_url_features(original)
        self.assertEqual(list(original.columns), ["url", "label"])
        self.assertIn("url_length", enriched.columns)

    def test_summary_has_one_row_per_label(self):
        data = pd.DataFrame(
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
        summary = build_summary(data)
        self.assertEqual(set(summary["label"]), {"legitima", "phishing"})


if __name__ == "__main__":
    unittest.main()
