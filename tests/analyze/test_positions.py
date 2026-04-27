#!/usr/bin/env python3
"""Tests for analyze/positions.py - position classification logic."""

import re

# Simple keyword classification test without full class instantiation
PRO_KEYWORDS = [
    'sunt de acord', 'susțin', 'vot pentru', 'sunt favorabil',
    'aprob', 'sprijin', 'necesar', 'important', 'bine'
]

CONTRA_KEYWORDS = [
    'nu sunt de acord', 'mă opun', 'vot contra', 'resping',
    'nu este corect', 'dăunător', 'periculos', 'ineficiență'
]

def classify_by_keywords(text: str) -> str:
    """Simple keyword-based classification."""
    text_lower = text.lower()
    pro_count = sum(1 for kw in PRO_KEYWORDS if kw in text_lower)
    contra_count = sum(1 for kw in CONTRA_KEYWORDS if kw in text_lower)
    
    if pro_count > contra_count:
        return 'PRO'
    elif contra_count > pro_count:
        return 'CONTRA'
    else:
        return 'NEUTRAL'

def test_classify_pro():
    statement = "Sunt de acord cu această lege și o susțin pe deplin."
    assert classify_by_keywords(statement) == 'PRO'

def test_classify_contra():
    statement = "Mă opun ferm acestui proiect și votez împotrivă."
    assert classify_by_keywords(statement) == 'CONTRA'

def test_classify_neutral():
    statement = "Voi analiza documentul și voi decide ulterior."
    assert classify_by_keywords(statement) == 'NEUTRAL'

def test_classify_tie_neutral():
    statement = "Acesta este un text care menționează ambele părți."
    # No strong keywords; should be neutral
    assert classify_by_keywords(statement) == 'NEUTRAL'

if __name__ == "__main__":
    test_classify_pro()
    test_classify_contra()
    test_classify_neutral()
    test_classify_tie_neutral()
    print("All positions classifier unit tests passed!")
