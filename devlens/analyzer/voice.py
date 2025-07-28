
import os
from pathlib import Path
import requests
from devlens.config import GROQ_API_KEY
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def generate_voice_summary(text: str, output_path: str = None):
    """Generate voice summary of code analysis using text-to-speech"""
    
    if not text or text.strip() == "":
        console.print("❌ No text provided for voice generation", style="red")
        return None
    
    if output_path is None:
        output_path = Path(__file__).parent.parent.parent / "output" / "voice_summary.wav"
        os.makedirs(output_path.parent, exist_ok=True)
    else:
        output_path = Path(output_path)
    
    console.print("🎤 Generating voice summary...", style="blue")
    try:
        text_output_path = output_path.with_suffix('.txt')
        
        with open(text_output_path, 'w', encoding='utf-8') as f:
            f.write(f"DevLens Voice Summary\n")
            f.write(f"==================\n\n")
            f.write(text)
        
        success_panel = Panel(
            f"✅ Voice summary text saved!\n📄 Saved to: {text_output_path}\n\n💡 Note: To generate actual audio, integrate with a TTS service like:\n• OpenAI TTS\n• ElevenLabs\n• Google Text-to-Speech\n• Azure Cognitive Services",
            title="🎉 Success",
            border_style="green",
            padding=(1, 2)
        )
        console.print(success_panel)
        
        return str(text_output_path)
        
    except Exception as e:
        error_panel = Panel(
            f"❌ Failed to generate voice summary: {str(e)}",
            title="⚠️ Error",
            border_style="red",
            padding=(1, 2)
        )
        console.print(error_panel)
        return None

def create_voice_friendly_summary(analysis_results: dict):
    """Create a voice-friendly version of the analysis results"""
    
    if not analysis_results:
        return "No analysis results available."
    
    voice_text = "DevLens Project Analysis Summary. "
    
    if 'total_files' in analysis_results:
        voice_text += f"This project contains {analysis_results['total_files']} files "
        voice_text += f"with {analysis_results['total_lines']} lines of code. "
    
    if 'languages' in analysis_results:
        languages = list(analysis_results['languages'].keys())
        if languages:
            if len(languages) == 1:
                voice_text += f"The project is written in {languages[0]}. "
            else:
                voice_text += f"The project uses {len(languages)} programming languages: "
                voice_text += f"{', '.join(languages[:-1])}, and {languages[-1]}. "
    
    if 'languages' in analysis_results and analysis_results['languages']:
        main_lang = max(analysis_results['languages'].items(), key=lambda x: x[1])
        voice_text += f"The primary language is {main_lang[0]} with {main_lang[1]} lines of code. "
    
    voice_text += "Analysis complete. Thank you for using DevLens."
    
    return voice_text
      