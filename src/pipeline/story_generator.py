"""Story generation pipeline using TinyStories-33M."""

from typing import Optional
from .data_structures import StoryRequest, ValidatedPrompt, GeneratedStory
from .validator import PromptValidator
from ..models.tinystories import TinyStoriesModel


class StoryGenerationPipeline:
    """Complete pipeline for generating children's stories."""
    
    # Length guidelines for token generation
    LENGTH_MAPPING = {
        "short": 400,    # ~2-3 paragraphs
        "medium": 600,   # ~4-5 paragraphs
        "long": 800,     # ~6-8 paragraphs
    }
    
    def __init__(self, model: Optional[TinyStoriesModel] = None):
        """Initialize the pipeline.
        
        Args:
            model: Pre-loaded TinyStories model (or will create new one)
        """
        self.validator = PromptValidator()
        self.model = model or TinyStoriesModel()
    
    def generate(self, request: StoryRequest) -> tuple[GeneratedStory, ValidatedPrompt]:
        """Generate a story from a request.
        
        Args:
            request: Story request from user
            
        Returns:
            Tuple of (generated story, validation info)
        """
        # Step 1: Validate and clean prompt
        validated = self.validator.validate(request)
        
        if not validated.is_safe:
            # Return a safe default story
            return self._create_safe_default_story(request, validated), validated
        
        # Step 2: Generate story with model
        max_length = self.LENGTH_MAPPING.get(request.story_length, 400)
        
        stories = self.model.generate_story(
            prompt=validated.cleaned_prompt,
            max_length=max_length,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.2,
            num_return_sequences=1
        )
        
        story_text = stories[0]
        
        # Step 3: Extract title and metadata
        title = self._extract_title(story_text)
        word_count = len(story_text.split())
        reading_time = self._calculate_reading_time(word_count)
        
        # Step 4: Create final story object
        generated_story = GeneratedStory(
            title=title,
            story_text=story_text,
            genre=request.genre,
            age_group=request.age_group,
            word_count=word_count,
            estimated_reading_time=reading_time,
            is_safe=True
        )
        
        return generated_story, validated
    
    def _extract_title(self, story_text: str) -> str:
        """Extract or generate a title from the story text.
        
        Args:
            story_text: The generated story
            
        Returns:
            A title for the story
        """
        # Look for title patterns in first few lines
        lines = [l.strip() for l in story_text.split('\n') if l.strip()]
        
        if lines:
            first_line = lines[0]
            # If first line is short and doesn't end with period, it might be a title
            if len(first_line) < 80 and not first_line.endswith('.'):
                return first_line
            
            # Check if there's a "Title:" pattern
            for line in lines[:3]:
                if line.lower().startswith('title:'):
                    return line[6:].strip()
        
        # Generate title from first sentence
        first_sentence = story_text.split('.')[0].strip()
        if 10 < len(first_sentence) < 100:
            return first_sentence
        
        # Default title
        return "A Wonderful Story"
    
    def _calculate_reading_time(self, word_count: int) -> str:
        """Calculate estimated reading time.
        
        Args:
            word_count: Number of words in the story
            
        Returns:
            Reading time estimate as string
        """
        # Children's reading speed: ~100-150 words per minute
        # Adult reading aloud: ~150-200 words per minute
        minutes = max(1, word_count // 150)
        return f"{minutes}-{minutes + 1} minutes"
    
    def _create_safe_default_story(
        self, 
        request: StoryRequest, 
        validated: ValidatedPrompt
    ) -> GeneratedStory:
        """Create a safe default story when validation fails.
        
        Args:
            request: Original request
            validated: Validation results
            
        Returns:
            A safe default story
        """
        default_text = (
            "Once upon a time, in a peaceful village, there lived a kind young child "
            "who loved to help others. Every day, they would share their toys with friends "
            "and learn new things about the world. Through friendship and kindness, "
            "they discovered that the greatest adventures come from caring for others. "
            "And they all lived happily ever after. The End."
        )
        
        return GeneratedStory(
            title="A Story About Kindness",
            story_text=default_text,
            genre=request.genre,
            age_group=request.age_group,
            word_count=len(default_text.split()),
            estimated_reading_time="2-3 minutes",
            is_safe=True
        )

