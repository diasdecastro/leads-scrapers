import sys
import os
import questionary
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.base_cli import EnricherCLI


class ImprintDataCLI(EnricherCLI):
    """CLI interface for Imprint Data enrichment."""
    
    @property
    def name(self) -> str:
        return "Imprint Data Enricher"
    
    @property
    def description(self) -> str:
        return "Extracts official company names and legal information from website imprint pages"
    
    def get_cli_params(self) -> Dict[str, Any]:
        """Get parameters for imprint data extraction."""
        print("\n📄 Configure imprint data extraction:")
        
        delay = questionary.text(
            "Delay between requests (seconds):",
            default="1.0"
        ).ask()
        
        if delay is None:
            return None
        
        method = questionary.select(
            "Extraction method:",
            choices=[
                questionary.Choice("regex", "Regex Pattern Matching (Fast)"),
                questionary.Choice("llm", "LLM-based Extraction (Requires Ollama)")
            ]
        ).ask()
        
        if method is None:
            return None
        
        params = {
            "delay": delay,
            "method": method
        }
        
        # Additional options for LLM method
        if method == "llm":
            model = questionary.text(
                "LLM model to use:",
                default="deepseek-r1:8b"
            ).ask()
            
            if model is None:
                return None
            
            params["model"] = model
            
            # Check if Ollama is available
            check_ollama = questionary.confirm(
                "Do you want to verify Ollama is running?",
                default=True
            ).ask()
            
            if check_ollama:
                print("💡 Make sure Ollama is running: ollama serve")
                print(f"💡 Make sure model is available: ollama pull {model}")
                
                continue_anyway = questionary.confirm(
                    "Continue with extraction?",
                    default=True
                ).ask()
                
                if not continue_anyway:
                    return None
        
        return params
    
    def build_command(self, params: Dict[str, Any]) -> list:
        """Build command for imprint data extraction."""
        # For imprint extraction, we'll run the extractor directly
        # since it has a different interface than the main.py scraping commands
        command = [
            sys.executable,
            "-c",
            f"""
import sys
import os
sys.path.append(os.getcwd())
from scrapers.imprint_data.scraper import OfficialNameExtractor

extractor = OfficialNameExtractor(llm_model="{params.get('model', 'deepseek-r1:8b')}")
extractor.run_enrichment(delay={params['delay']}, method="{params['method']}")
"""
        ]
        
        return command