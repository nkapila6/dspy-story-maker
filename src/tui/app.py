"""Terminal User Interface for story generation."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich import box
import time
from typing import Optional

from ..pipeline.story_generator import StoryGenerationPipeline
from ..pipeline.data_structures import StoryRequest, GeneratedStory
from ..models.tinystories import TinyStoriesModel


class StoryTUI:
    """Terminal User Interface for interactive story generation."""
    
    GENRES = [
        "adventure",
        "fantasy", 
        "friendship",
        "learning",
        "animals",
        "bedtime",
        "funny",
        "mystery",
    ]
    
    AGE_GROUPS = [
        "3-5",
        "5-7",
        "7-10",
    ]
    
    STORY_LENGTHS = [
        "short",
        "medium",
        "long",
    ]
    
    def __init__(self):
        """Initialize the TUI."""
        self.console = Console()
        self.pipeline: Optional[StoryGenerationPipeline] = None
    
    def run(self):
        """Run the main TUI loop."""
        self.show_welcome()
        
        # Load model with progress indicator
        self.load_model()
        
        # Main story generation loop
        while True:
            try:
                self.console.print()
                story, validated = self.create_story()
                
                if story:
                    self.display_story(story, validated)
                
                self.console.print()
                if not Confirm.ask("[bold cyan]Generate another story?[/]", default=True):
                    self.show_goodbye()
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted by user[/]")
                self.show_goodbye()
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/] {e}")
                if not Confirm.ask("Try again?", default=True):
                    break
    
    def show_welcome(self):
        """Display welcome screen."""
        self.console.clear()
        
        welcome_text = Text()
        welcome_text.append("✨ ", style="bold yellow")
        welcome_text.append("Magical Story Generator", style="bold magenta")
        welcome_text.append(" ✨", style="bold yellow")
        
        welcome_panel = Panel(
            Text.from_markup(
                "[cyan]Welcome to the AI-powered story generator![/]\n\n"
                "Using TinyStories-33M to create wonderful bedtime stories\n"
                "for children. Just tell me what kind of story you'd like!\n\n"
                "[dim]Powered by TinyStories-33M 🤖[/]"
            ),
            title=welcome_text,
            border_style="magenta",
            box=box.DOUBLE,
            padding=(1, 2),
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def show_goodbye(self):
        """Display goodbye message."""
        self.console.print()
        goodbye_panel = Panel(
            "[bold cyan]Thank you for using Magical Story Generator![/]\n"
            "[yellow]Sweet dreams! 🌙✨[/]",
            border_style="cyan",
            box=box.ROUNDED,
        )
        self.console.print(goodbye_panel)
    
    def load_model(self):
        """Load the TinyStories model with progress indicator."""
        self.console.print("[bold yellow]Loading TinyStories-33M model...[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Downloading and initializing model...", total=None)
            
            try:
                model = TinyStoriesModel()
                self.pipeline = StoryGenerationPipeline(model=model)
                progress.update(task, completed=True)
            except Exception as e:
                self.console.print(f"[bold red]Failed to load model:[/] {e}")
                raise
        
        self.console.print("[bold green]✓ Model ready![/]")
    
    def create_story(self) -> tuple[Optional[GeneratedStory], Optional[object]]:
        """Interactive story creation flow."""
        # Get genre
        genre = self.select_genre()
        if not genre:
            return None, None
        
        # Get story prompt
        prompt = self.get_story_prompt()
        if not prompt:
            return None, None
        
        # Get age group
        age_group = self.select_age_group()
        
        # Get story length
        length = self.select_length()
        
        # Create request
        request = StoryRequest(
            prompt=prompt,
            genre=genre,
            age_group=age_group,
            story_length=length
        )
        
        # Show confirmation
        self.show_request_summary(request)
        
        if not Confirm.ask("[bold cyan]Generate this story?[/]", default=True):
            return None, None
        
        # Generate story
        return self.generate_with_progress(request)
    
    def select_genre(self) -> Optional[str]:
        """Let user select a story genre."""
        self.console.print("\n[bold cyan] Select a genre:[/]")
        
        # Create a nice table of genres
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Number", style="cyan")
        table.add_column("Genre", style="yellow")
        
        for i, genre in enumerate(self.GENRES, 1):
            table.add_row(f"{i}.", genre.capitalize())
        
        self.console.print(table)
        
        while True:
            choice = Prompt.ask(
                "[cyan]Enter genre number[/]",
                choices=[str(i) for i in range(1, len(self.GENRES) + 1)],
                show_choices=False
            )
            
            if choice:
                return self.GENRES[int(choice) - 1]
            return None
    
    def get_story_prompt(self) -> Optional[str]:
        """Get story prompt from user."""
        self.console.print("\n[bold cyan]📝 What should the story be about?[/]")
        self.console.print("[dim]Example: A brave little mouse who explores a magical garden[/]")
        
        prompt = Prompt.ask("[cyan]Your story idea[/]")
        return prompt.strip() if prompt else None
    
    def select_age_group(self) -> str:
        """Let user select target age group."""
        self.console.print("\n[bold cyan] Select age group:[/]")
        
        for i, age in enumerate(self.AGE_GROUPS, 1):
            self.console.print(f"  [cyan]{i}.[/] {age} years old")
        
        choice = Prompt.ask(
            "[cyan]Enter age group number[/]",
            choices=[str(i) for i in range(1, len(self.AGE_GROUPS) + 1)],
            default="2",
            show_default=True,
            show_choices=False
        )
        
        return self.AGE_GROUPS[int(choice) - 1]
    
    def select_length(self) -> str:
        """Let user select story length."""
        self.console.print("\n[bold cyan] Select story length:[/]")
        
        for i, length in enumerate(self.STORY_LENGTHS, 1):
            self.console.print(f"  [cyan]{i}.[/] {length.capitalize()}")
        
        choice = Prompt.ask(
            "[cyan]Enter length number[/]",
            choices=[str(i) for i in range(1, len(self.STORY_LENGTHS) + 1)],
            default="1",
            show_default=True,
            show_choices=False
        )
        
        return self.STORY_LENGTHS[int(choice) - 1]
    
    def show_request_summary(self, request: StoryRequest):
        """Show summary of the story request."""
        self.console.print()
        
        summary = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
        summary.add_column("Field", style="bold cyan")
        summary.add_column("Value", style="yellow")
        
        summary.add_row("Genre", request.genre.capitalize())
        summary.add_row("Prompt", request.prompt)
        summary.add_row("Age Group", request.age_group)
        summary.add_row("Length", request.story_length.capitalize())
        
        self.console.print(Panel(summary, title="[bold]Story Request[/]", border_style="cyan"))
    
    def generate_with_progress(self, request: StoryRequest) -> tuple[Optional[GeneratedStory], Optional[object]]:
        """Generate story with progress indicator."""
        self.console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]✨ Generating your magical story...", total=None)
            
            try:
                story, validated = self.pipeline.generate(request)
                progress.update(task, completed=True)
                
                # Show any warnings
                if validated.warnings:
                    self.console.print()
                    for warning in validated.warnings:
                        self.console.print(f"[yellow]⚠ {warning}[/]")
                
                return story, validated
                
            except Exception as e:
                self.console.print(f"[bold red]Failed to generate story:[/] {e}")
                return None, None
    
    def display_story(self, story: GeneratedStory, validated: Optional[object]):
        """Display the generated story in a beautiful format."""
        self.console.print("\n")
        
        # Story header
        header = Text()
        # header.append("📖 ", style="bold yellow")
        header.append(story.title, style="bold magenta")
        
        # Story metadata
        metadata = Text()
        metadata.append(f"Genre: {story.genre.capitalize()}  ", style="cyan")
        metadata.append(f"•  ", style="dim")
        metadata.append(f"Age: {story.age_group}  ", style="cyan")
        metadata.append(f"•  ", style="dim")
        metadata.append(f"Reading time: {story.estimated_reading_time}", style="cyan")
        
        # Story content panel
        story_panel = Panel(
            story.story_text,
            title=header,
            subtitle=metadata,
            border_style="magenta",
            box=box.DOUBLE,
            padding=(1, 2),
        )
        
        self.console.print(story_panel)
        
        # Stats
        stats_text = Text()
        stats_text.append(f"📊 Words: {story.word_count}  ", style="dim cyan")
        if validated and validated.removed_content:
            stats_text.append(f"🛡️ Safety filters applied  ", style="dim yellow")
        
        self.console.print(stats_text)


def main():
    """Main entry point for the TUI application."""
    try:
        app = StoryTUI()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

