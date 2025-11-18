"""Prompt validation and safety checking."""

import re
from typing import Tuple
from .data_structures import StoryRequest, ValidatedPrompt


class PromptValidator:
    """Validates and cleans user prompts for child safety."""
    
    def __init__(self):
        """Initialize the validator with harmful content patterns."""
        self.harmful_patterns = [
            r'\b(kill|death|die|murder|suicide)\b',
            r'\b(violence|fighting|war|gun|weapon|blood|gore)\b',
            r'\b(hate|racist|discrimination)\b',
            r'\b(scary|frightening|nightmare|terror|horror)\b',
            r'\b(inappropriate|adult|sexual)\b',
        ]
        
        # Gentler alternatives for replacement
        self.replacements = {
            r'\b(scary|frightening|terror|horror)\b': 'mysterious',
            r'\b(fight|fighting)\b': 'disagree',
            r'\b(hurt|pain)\b': 'uncomfortable',
            r'\b(angry|mad)\b': 'upset',
            r'\b(bad|evil)\b': 'mischievous',
        }
    
    def validate(self, request: StoryRequest) -> ValidatedPrompt:
        """Validate and clean a story request.
        
        Args:
            request: The story request to validate
            
        Returns:
            ValidatedPrompt with safety information
        """
        prompt = request.prompt
        removed_content = []
        warnings = []
        is_safe = True
        
        # Check for harmful content
        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, prompt.lower())
            if matches:
                removed_content.extend(matches)
                is_safe = False
                warnings.append(f"Removed potentially inappropriate content: {', '.join(set(matches))}")
        
        # Clean the prompt
        cleaned_prompt = prompt
        for pattern, replacement in self.replacements.items():
            cleaned_prompt = re.sub(pattern, replacement, cleaned_prompt, flags=re.IGNORECASE)
        
        # If severely unsafe, replace with generic prompt
        if not is_safe and len(removed_content) > 3:
            cleaned_prompt = f"A gentle {request.genre} story about friendship and kindness"
            warnings.append("Prompt was significantly modified for safety")
        
        # Enhance the prompt with genre context
        if is_safe or len(removed_content) <= 3:
            cleaned_prompt = self._enhance_prompt(cleaned_prompt, request.genre)
        
        return ValidatedPrompt(
            original_prompt=prompt,
            cleaned_prompt=cleaned_prompt,
            is_safe=is_safe or len(removed_content) <= 3,  # Allow minor issues
            removed_content=list(set(removed_content)),
            warnings=warnings
        )
    
    def _enhance_prompt(self, prompt: str, genre: str) -> str:
        """Enhance the prompt with genre-specific context.
        
        Args:
            prompt: Cleaned prompt
            genre: Story genre
            
        Returns:
            Enhanced prompt for better story generation
        """
        # Add genre context to help the model
        genre_starters = {
            "adventure": "Once upon a time, in a land of exciting adventures, ",
            "fantasy": "In a magical world filled with wonder, ",
            "friendship": "In a warm and friendly place, ",
            "learning": "One day, a curious child discovered that ",
            "animals": "In a forest where animals could talk, ",
            "bedtime": "As the stars began to twinkle in the night sky, ",
            "funny": "On a silly and wonderful day, ",
            "mystery": "There was an interesting mystery to solve when ",
        }
        
        starter = genre_starters.get(genre.lower(), "Once upon a time, ")
        
        # Only add starter if prompt doesn't already have a story beginning
        if not any(prompt.lower().startswith(p) for p in ["once", "there", "in a", "one day"]):
            return starter + prompt.lower()
        
        return prompt

