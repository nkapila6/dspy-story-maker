"""Data structures for the story generation pipeline."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StoryRequest:
    """User's story request."""
    prompt: str
    genre: str
    age_group: str = "3-7"
    story_length: str = "short"
    
    
@dataclass
class ValidatedPrompt:
    """Cleaned and validated prompt."""
    original_prompt: str
    cleaned_prompt: str
    is_safe: bool
    removed_content: list[str]
    warnings: list[str]


@dataclass
class GeneratedStory:
    """Generated story with metadata."""
    title: str
    story_text: str
    genre: str
    age_group: str
    word_count: int
    estimated_reading_time: str
    is_safe: bool
    
    def get_reading_time(self) -> str:
        """Calculate estimated reading time based on word count."""
        # Average reading speed: ~200 words per minute for children's stories
        minutes = max(1, self.word_count // 200)
        return f"{minutes}-{minutes + 2} minutes"

