import typer
from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.summary import display_code_summary
from devlens.analyzer.readme_gen import generate_readme
from devlens.analyzer.voice import generate_voice_summary, create_voice_friendly_summary

app = typer.Typer()

@app.command()
def analyze(path: str = typer.Argument(".", help="Path to analyze")):
    """Analyze code with AI-powered summaries"""
    summarize_code(path)

@app.command()
def summary(path: str = typer.Argument(".", help="Path to summarize")):
    """Generate comprehensive project summary"""
    display_code_summary(path)

@app.command()
def stats(path: str = typer.Argument(".", help="Path to get statistics")):
    """Quick project statistics"""
    display_code_summary(path)

@app.command()
def readme(path: str = typer.Argument(".", help="Path to generate README for")):
    """Generate a professional README.md file"""
    generate_readme(path)

@app.command()
def voice(
    path: str = typer.Argument(".", help="Path to generate voice summary for"),
    voice_type: str = typer.Option("alloy", help="Voice type: alloy, echo, fable, onyx, nova, shimmer")
):
    """Generate a voice audio summary of the project"""
    from devlens.analyzer.summary import count_lines_by_language
    
    # Get project data
    line_counts, file_counts = count_lines_by_language(path)
    
    # Create analysis results dict
    analysis_results = {
        'total_files': sum(file_counts.values()),
        'total_lines': sum(line_counts.values()),
        'languages': line_counts,
        'file_counts': file_counts
    }
    
    # Generate voice-friendly text
    voice_text = create_voice_friendly_summary(analysis_results)
    
    # Generate actual voice audio
    generate_voice_summary(voice_text, voice=voice_type)


def main():
    app()

if __name__ == "__main__":
    main()