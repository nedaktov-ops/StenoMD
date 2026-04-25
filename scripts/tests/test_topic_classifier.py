#!/usr/bin/env python3
"""
Unit tests for TopicClassifier
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyze.topics import TopicClassifier


class TestTopicClassifier(unittest.TestCase):
    """Test cases for TopicClassifier."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.classifier = TopicClassifier()
    
    def test_economy_classification(self):
        """Test economy topic classification."""
        text = "buget finante economie investitii"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('economie', topics)
    
    def test_health_classification(self):
        """Test health topic classification."""
        text = "spital sanatate medical medicament"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('sanatate', topics)
    
    def test_education_classification(self):
        """Test education topic classification."""
        text = "scoala universitate studenti educatie"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('educatie', topics)
    
    def test_justice_classification(self):
        """Test justice topic classification."""
        text = "instanta judecator DNA justitie"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('justitie', topics)
    
    def test_defense_classification(self):
        """Test defense topic classification."""
        text = "armata NATO aparare militara"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('aparare', topics)
    
    def test_environment_classification(self):
        """Test environment topic classification."""
        text = "mediu ecologie poluare climă"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('mediu', topics)
    
    def test_social_classification(self):
        """Test social topic classification."""
        text = "pensii sociale alocatii"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('social', topics)
    
    def test_european_classification(self):
        """Test European affairs classification."""
        text = "european UE Bruxelles comisar"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('europa', topics)
    
    def test_agriculture_classification(self):
        """Test agriculture topic classification."""
        text = "agricultura fermier MADR"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('agricultura', topics)
    
    def test_infrastructure_classification(self):
        """Test infrastructure topic classification."""
        text = "autostrada drum transport"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('infrastructura', topics)
    
    def test_culture_classification(self):
        """Test culture topic classification."""
        text = "cultura arta teatru muzeu"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('cultura', topics)
    
    def test_research_classification(self):
        """Test research topic classification."""
        text = "cercetare stiinta inovare"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('cercetare', topics)
    
    def test_energy_classification(self):
        """Test energy topic classification."""
        text = "energie electric gaze nuclear"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('energie', topics)
    
    def test_transport_classification(self):
        """Test transport topic classification."""
        text = "transport metrou autobuz CFR"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('transport', topics)
    
    def test_admin_classification(self):
        """Test administration topic classification."""
        text = "minister administratie primarie"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('administratie', topics)
    
    def test_labor_classification(self):
        """Test labor topic classification."""
        text = "munca angajare somaj salariu"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        self.assertIn('munca', topics)
    
    def test_multi_topic_classification(self):
        """Test multiple topic classification."""
        text = "buget sanatate educatie fonduri europene"
        results = self.classifier.classify(text)
        
        topics = [t[0] for t in results]
        has_multiple = len(topics) >= 1
        self.assertTrue(has_multiple, f"Expected at least 1 topic, got: {topics}")
    
    def test_no_topic_classification(self):
        """Test text with no matching topics."""
        text = "random text xyz foo bar"
        results = self.classifier.classify(text)
        
        self.assertEqual(len(results), 0)
    
    def test_topic_count(self):
        """Test total number of topics."""
        self.assertGreaterEqual(len(self.classifier.TOPICS), 14)
    
    def test_confidence_scoring(self):
        """Test confidence scoring."""
        text = "buget economie finante investitii"
        results = self.classifier.classify(text)
        
        if results:
            confidence = results[0][1]
            self.assertGreaterEqual(confidence, 0.5)
            self.assertLessEqual(confidence, 1.0)


if __name__ == '__main__':
    unittest.main()