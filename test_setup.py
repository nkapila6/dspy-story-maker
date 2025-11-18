#!/usr/bin/env python3
"""Quick test to verify the setup is working."""

import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_imports():
    """Test that all required imports work."""
    console.print("[cyan]Testing imports...[/]")
    
    try:
        import torch
        console.print("✓ PyTorch imported", style="green")
        
        import transformers
        console.print("✓ Transformers imported", style="green")
        
        import rich
        console.print("✓ Rich imported", style="green")
        
        from src.models.tinystories import TinyStoriesModel
        console.print("✓ TinyStoriesModel imported", style="green")
        
        from src.pipeline.story_generator import StoryGenerationPipeline
        console.print("✓ StoryGenerationPipeline imported", style="green")
        
        from src.tui.app import StoryTUI
        console.print("✓ StoryTUI imported", style="green")
        
        console.print("\n[bold green]✓ All imports successful![/]")
        
        # Check device
        console.print(f"\n[cyan]PyTorch device check:[/]")
        if torch.backends.mps.is_available():
            console.print("✓ MPS (Metal Performance Shaders) available - will use GPU acceleration", style="green")
        else:
            console.print("○ MPS not available - will use CPU", style="yellow")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]✗ Import failed: {e}[/]")
        return False

def main():
    """Run setup tests."""
    console.print(Panel.fit(
        "[bold cyan]Story Generator Setup Test[/]\n"
        "Verifying all components are installed correctly...",
        border_style="cyan"
    ))
    console.print()
    
    if test_imports():
        console.print()
        console.print(Panel.fit(
            "[bold green]Setup complete![/]\n\n"
            "You can now run the story generator with:\n"
            "[cyan]python main.py[/]",
            border_style="green"
        ))
        return 0
    else:
        console.print()
        console.print(Panel.fit(
            "[bold red]Setup failed![/]\n\n"
            "Please check the error messages above and try:\n"
            "[cyan]uv sync[/]",
            border_style="red"
        ))
        return 1

if __name__ == "__main__":
    sys.exit(main())

