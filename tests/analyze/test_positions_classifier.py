#!/usr/bin/env python3
"""Tests for analyze/positions.py - PositionClassifier class."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from analyze.positions import PositionClassifier, Classification


def test_classify_with_keywords_pro():
    classifier = PositionClassifier()
    # Override init to avoid DB
    classifier.ollama_model = None
    text = "Sunt de acord cu această lege și o susțin pe deplin."
    position, keywords = classifier.classify_with_keywords(text)
    assert position == 'PRO'
    assert len(keywords) > 0
    assert any('susțin' in kw for kw in keywords)


def test_classify_with_keywords_contra():
    classifier = PositionClassifier()
    classifier.ollama_model = None
    text = "Mă opun ferm acestui proiect și votez împotrivă."
    position, keywords = classifier.classify_with_keywords(text)
    assert position == 'CONTRA'
    assert any('opun' in kw.lower() or 'împotrivă' in kw.lower() for kw in keywords)


def test_classify_with_keywords_neutral_no_match():
    classifier = PositionClassifier()
    classifier.ollama_model = None
    text = "Voi analiza documentul și voi decide ulterior."
    position, keywords = classifier.classify_with_keywords(text)
    assert position == 'NEUTRAL'
    assert keywords == []


def test_classify_with_keywords_tie():
    classifier = PositionClassifier()
    classifier.ollama_model = None
    # Text with exactly one PRO and one CONTRA keyword -> NEUTRAL
    text = 'Susțin. Mă opun.'
    position, keywords = classifier.classify_with_keywords(text)
    assert position == 'NEUTRAL'
    # Both keywords should be found
    assert 'susțin' in [k.lower() for k in keywords]
    assert any('opun' in k.lower() for k in keywords)


def test_classify_method_returns_Classification():
    classifier = PositionClassifier()
    classifier.ollama_model = None
    # Mock _init_db to do nothing
    with patch.object(PositionClassifier, '_init_db', return_value=None):
        classifier._init_db = lambda: None  # no-op
        result = classifier.classify("stmt1", "Ion Popescu", "Sunt de acord cu legea.")
        assert isinstance(result, Classification)
        assert result.statement_id == "stmt1"
        assert result.speaker == "Ion Popescu"
        assert result.position == 'PRO'
        assert result.method == 'keyword'
        assert result.confidence > 0.5
        assert len(result.keywords_found) > 0


def test_classify_default_when_no_keywords():
    classifier = PositionClassifier()
    classifier.ollama_model = None
    with patch.object(PositionClassifier, '_init_db', return_value=None):
        classifier._init_db = lambda: None
        result = classifier.classify("stmt2", "Ana", "Nicio expresie cheie.")
        assert result.position == 'NEUTRAL'
        assert result.method == 'default'
        assert result.confidence == 0.3
        assert result.keywords_found == []


def test_classify_ollama_used_when_ambiguous_and_enabled():
    classifier = PositionClassifier()
    # Simulate ollama available
    classifier.ollama_model = 'phi3'
    with patch.object(PositionClassifier, '_init_db', return_value=None):
        classifier._init_db = lambda: None
        # Mock classify_with_ollama to return PRO
        with patch.object(classifier, 'classify_with_ollama', return_value='PRO') as mock_ollama:
            result = classifier.classify("stmt3", "Speaker", "Some ambiguous text", use_ollama_if_ambiguous=True)
            mock_ollama.assert_called_once()
            assert result.position == 'PRO'
            assert result.method == 'ollama'
            assert result.confidence == 0.6

if __name__ == "__main__":
    test_classify_with_keywords_pro()
    test_classify_with_keywords_contra()
    test_classify_with_keywords_neutral_no_match()
    test_classify_with_keywords_tie()
    test_classify_method_returns_Classification()
    test_classify_default_when_no_keywords()
    test_classify_ollama_used_when_ambiguous_and_enabled()
    print("All PositionClassifier tests passed!")
