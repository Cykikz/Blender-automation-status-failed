 """
Blender AI Automation Package

This package provides tools to generate Blender 3D content from natural language
using AI (Claude, ChatGPT, or local LLMs).
"""

from .config import Config
from .prompt_processor import PromptProcessor, process_prompt
from .ai_generator import AIGenerator, generate
from .code_validator import CodeValidator, validate_code
from .blender_executor import BlenderExecutor

__version__ = "1.0.0"
__all__ = [
    'Config',
    'PromptProcessor',
    'process_prompt',
    'AIGenerator',
    'generate',
    'CodeValidator',
    'validate_code',
    'BlenderExecutor',
]
