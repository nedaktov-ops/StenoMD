#!/usr/bin/env python3
"""
StenoMD Statement Extractor
Extracts key statements from speakers with first 200 chars
"""

import re
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class Statement:
    """A single statement from a speaker."""
    speaker: str
    text: str
    word_count: int
    excerpt: str
    position: Optional[str] = None
    topic: Optional[str] = None


class StatementExtractor:
    """Extract statements from stenogram transcript."""
    
    SPEAKER_PATTERN = re.compile(
        r'(?:Domnul|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ]\.?)?(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)+)',
        re.I
    )
    
    def __init__(self):
        self.statements: List[Statement] = []
    
    def extract(
        self, transcript: str, speaker_name: Optional[str] = None,
        max_chars: int = 200
    ) -> List[Statement]:
        """
        Extract statements from transcript.
        
        If speaker_name is provided, extract only their statements.
        Otherwise, extract all statements.
        """
        if not transcript:
            return []
        
        statements = []
        speaker_name_lower = speaker_name.lower() if speaker_name else None
        
        # Split transcript into speaker blocks
        speaker_blocks = self._split_by_speaker(transcript)
        
        for speaker, text in speaker_blocks:
            if speaker_name_lower and speaker.lower() != speaker_name_lower:
                continue
            
            word_count = len(text.split())
            excerpt = text[:max_chars].strip()
            
            if len(excerpt) < 20:
                continue
            
            statements.append(Statement(
                speaker=speaker,
                text=text,
                word_count=word_count,
                excerpt=excerpt,
            ))
        
        self.statements = statements
        return statements
    
    def _split_by_speaker(self, transcript: str) -> List[tuple]:
        """Split transcript by speaker names."""
        blocks = []
        current_speaker = None
        current_text = []
        
        for match in self.SPEAKER_PATTERN.finditer(transcript):
            speaker = match.group(1)
            
            # New speaker
            if current_speaker is not None and current_speaker != speaker:
                text = ' '.join(current_text)
                if text.strip():
                    blocks.append((current_speaker, text))
                current_text = []
            
            current_speaker = speaker
            
            # Get text after speaker name (until next speaker or end)
            start = match.end()
            end = self._find_next_speaker_start(transcript, match.end())
            current_text.append(transcript[start:end].strip())
        
        # Add last speaker's text
        if current_speaker and current_text:
            text = ' '.join(current_text)
            if text.strip():
                blocks.append((current_speaker, text))
        
        return blocks
    
    def _find_next_speaker_start(self, text: str, start: int) -> int:
        """Find where next speaker mention starts."""
        search = text[start:start + 2000]
        match = self.SPEAKER_PATTERN.search(search)
        if match:
            return start + match.start()
        return len(text)
    
    def get_first_statement(self, transcript: str, speaker_name: str) -> Optional[Statement]:
        """Get first statement from a specific speaker."""
        statements = self.extract(transcript, speaker_name)
        return statements[0] if statements else None
    
    def get_speaker_count(self, transcript: str) -> int:
        """Count unique speakers in transcript."""
        speakers = set()
        for match in self.SPEAKER_PATTERN.finditer(transcript):
            speakers.add(match.group(1))
        return len(speakers)
    
    def get_statement_count(self, transcript: str, speaker_name: str) -> int:
        """Count statements from a specific speaker."""
        count = 0
        for match in self.SPEAKER_PATTERN.finditer(transcript):
            if match.group(1).lower() == speaker_name.lower():
                count += 1
        return count


def extract_statements(transcript: str, speaker: Optional[str] = None) -> List[Statement]:
    """Standalone statement extraction."""
    extractor = StatementExtractor()
    return extractor.extract(transcript, speaker)


if __name__ == '__main__':
    extractor = StatementExtractor()
    
    test_transcript = """
    Domnul Mihai Coteț: Începem cu Propunerea legislativă pentru completarea Legii nr.227/2015 privind Codul fiscal. Aceasta este o inițiativă importantă pentru sistemul nostru bugetar.
    
    Domnul Vasile Blaga: Sunt de acord cu colegul meu. Trebuie să aprobăm această lege cât mai curând posibil.
    
    Doamna Niculina Stelea: Am câteva amendamente la acest proiect de lege. Propun includerea unor prevederi suplimentare pentru transparență.
    """
    
    print("=== Statement Extractor Tests ===")
    print(f"Unique speakers: {extractor.get_speaker_count(test_transcript)}")
    
    statements = extractor.extract(test_transcript)
    print(f"Statements extracted: {len(statements)}")
    
    for stmt in statements:
        print(f"\n{stmt.speaker}:")
        print(f"  Words: {stmt.word_count}")
        print(f"  Excerpt: {stmt.excerpt[:60]}...")