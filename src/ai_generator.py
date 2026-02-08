 """
AI Generator Module

Handles interaction with AI providers (Claude, OpenAI, Local LLMs)
to generate Blender Python code from natural language prompts.
"""

import logging
from pathlib import Path
from typing import Optional, Dict
import anthropic
import openai
import requests

from config import Config

logger = logging.getLogger(__name__)


class AIGenerator:
    """Generates Blender Python code using AI"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI Generator
        
        Args:
            provider (str, optional): AI provider ('claude', 'openai', 'local')
                                     If None, uses Config.AI_PROVIDER
        """
        self.provider = provider or Config.AI_PROVIDER
        self.client = None
        
        # Initialize the appropriate client
        if self.provider == "claude":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set in .env")
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            logger.info("Initialized Claude AI client")
            
        elif self.provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in .env")
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai
            logger.info("Initialized OpenAI client")
            
        elif self.provider == "local":
            logger.info(f"Using local LLM at {Config.LOCAL_LLM_URL}")
            
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")
    
    def load_system_prompt(self, prompt_type: str = "base") -> str:
        """
        Load system prompt from file
        
        Args:
            prompt_type (str): Type of prompt to load
            
        Returns:
            str: System prompt content
        """
        prompt_file = Config.get_prompt_file(prompt_type)
        
        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}, using base prompt")
            prompt_file = Config.get_prompt_file("base")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded system prompt from {prompt_file.name}")
            return content
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if file loading fails"""
        return """You are an expert Blender Python (bpy) developer.
Generate clean, working Python code for Blender based on user descriptions.

Requirements:
- Always clear existing objects first
- Import necessary modules (bpy, math, mathutils)
- Add clear comments
- Use realistic scales
- Return ONLY Python code in a code block
- No explanations outside the code block

Format:
```python
import bpy
# Your code here
```
"""
    
    def generate_code(
        self,
        user_prompt: str,
        prompt_type: str = "base",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate Blender Python code from user prompt
        
        Args:
            user_prompt (str): User's natural language description
            prompt_type (str): Type of specialized prompt to use
            temperature (float, optional): Generation temperature
            max_tokens (int, optional): Maximum tokens to generate
            
        Returns:
            str: Generated Python code
        """
        temperature = temperature or Config.TEMPERATURE
        max_tokens = max_tokens or Config.MAX_TOKENS
        
        # Load appropriate system prompt
        system_prompt = self.load_system_prompt(prompt_type)
        
        logger.info(f"Generating code with {self.provider} for: {user_prompt[:50]}...")
        
        try:
            if self.provider == "claude":
                code = self._generate_claude(user_prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "openai":
                code = self._generate_openai(user_prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "local":
                code = self._generate_local(user_prompt, system_prompt, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Clean the code
            cleaned_code = self._clean_code(code)
            logger.info("Code generation successful")
            
            return cleaned_code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise
    
    def _generate_claude(
        self,
        user_prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate code using Claude API"""
        message = self.client.messages.create(
            model=Config.CLAUDE_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return message.content[0].text
    
    def _generate_openai(
        self,
        user_prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate code using OpenAI API"""
        response = self.client.ChatCompletion.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_local(
        self,
        user_prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate code using local LLM (Ollama, etc.)"""
        full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}\n\nGenerate the Python code:"
        
        payload = {
            "model": Config.LOCAL_LLM_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(Config.LOCAL_LLM_URL, json=payload)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _clean_code(self, raw_code: str) -> str:
        """
        Clean generated code by removing markdown formatting
        
        Args:
            raw_code (str): Raw code from AI
            
        Returns:
            str: Cleaned Python code
        """
        code = raw_code.strip()
        
        # Remove markdown code blocks
        if "```python" in code:
            # Extract code between ```python and ```
            parts = code.split("```python")
            if len(parts) > 1:
                code = parts[1].split("```")[0].strip()
        elif "```" in code:
            # Extract code between ``` and ```
            parts = code.split("```")
            if len(parts) >= 3:
                code = parts[1].strip()
        
        # Remove common prefixes
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that look like markdown or comments about the code
            if line.strip().startswith('#') and any(word in line.lower() for word in ['here', 'this', 'above', 'below']):
                continue
            cleaned_lines.append(line)
        
        code = '\n'.join(cleaned_lines)
        
        return code
    
    def refine_code(
        self,
        original_code: str,
        feedback: str,
        prompt_type: str = "base"
    ) -> str:
        """
        Refine existing code based on user feedback
        
        Args:
            original_code (str): Original generated code
            feedback (str): User's feedback/requested changes
            prompt_type (str): Type of prompt to use
            
        Returns:
            str: Refined Python code
        """
        system_prompt = self.load_system_prompt(prompt_type)
        
        refinement_prompt = f"""Here's the current Blender Python code:

```python
{original_code}
```

User feedback: {feedback}

Please provide the complete updated code with the requested changes.
Return ONLY the Python code, no explanations."""
        
        logger.info(f"Refining code based on feedback: {feedback[:50]}...")
        
        return self.generate_code(
            refinement_prompt,
            prompt_type=prompt_type
        )
    
    def generate_with_context(
        self,
        user_prompt: str,
        context: Dict[str, any],
        prompt_type: str = "base"
    ) -> str:
        """
        Generate code with additional context
        
        Args:
            user_prompt (str): User's prompt
            context (dict): Additional context (previous generations, scene state, etc.)
            prompt_type (str): Type of prompt to use
            
        Returns:
            str: Generated Python code
        """
        # Build enhanced prompt with context
        enhanced_prompt = user_prompt
        
        if context.get('previous_code'):
            enhanced_prompt = f"""Previous code in the scene:
```python
{context['previous_code']}
```

New request: {user_prompt}

Generate code that works with the existing scene."""
        
        if context.get('objects'):
            enhanced_prompt += f"\n\nExisting objects: {', '.join(context['objects'])}"
        
        return self.generate_code(enhanced_prompt, prompt_type)


# Convenience function for quick generation
def generate(prompt: str, prompt_type: str = "base") -> str:
    """
    Quick generation function
    
    Args:
        prompt (str): User prompt
        prompt_type (str): Type of prompt to use
        
    Returns:
        str: Generated code
    """
    generator = AIGenerator()
    return generator.generate_code(prompt, prompt_type)
