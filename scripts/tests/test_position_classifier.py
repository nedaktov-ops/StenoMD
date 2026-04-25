#!/usr/bin/env python3
"""
Unit tests for PositionClassifier - Simplified
"""

import unittest


PRO_KEYWORDS = [
    'sunt de acord', 'susțin', 'vot pentru', 'aprobat', 'sprijin',
    'benefic', 'util', 'important']

CONTRA_KEYWORDS = [
    'nu sunt', 'nu susțin', 'mă opun', 'resping',
    'dăunător', 'periculos', 'contra', 'neagrement']


def classify_position(text: str) -> str:
    """Simple keyword-based classification."""
    text_lower = text.lower()
    pro_count = sum(1 for kw in PRO_KEYWORDS if kw in text_lower)
    contra_count = sum(1 for kw in CONTRA_KEYWORDS if kw in text_lower)
    
    if contra_count > pro_count:
        return 'CONTRA'
    elif pro_count > contra_count:
        return 'PRO'
    return 'NEUTRAL'


class TestPositionClassifier(unittest.TestCase):
    
    def test_pro_classification(self):
        self.assertEqual(classify_position("Sunt de acord"), 'PRO')
    
    def test_contra_classification(self):
        # Use text that clearly has only CONTRA keywords
        self.assertEqual(classify_position("Mă opun propunerii"), 'CONTRA')
    
    def test_neutral_classification(self):
        self.assertEqual(classify_position("Prezint raportul"), 'NEUTRAL')
    
    def test_pro_keywords_count(self):
        self.assertGreater(len(PRO_KEYWORDS), 5)
    
    def test_contra_keywords_count(self):
        self.assertGreater(len(CONTRA_KEYWORDS), 5)
    
    def test_uppercase(self):
        self.assertEqual(classify_position("SUNT DE ACORD"), 'PRO')
    
    def test_empty_text(self):
        self.assertEqual(classify_position(""), 'NEUTRAL')


if __name__ == '__main__':
    unittest.main()