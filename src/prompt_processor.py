import logging
import re
from typing import Tuple, Dict, List, Optional

from config import Config

logger = logging.getLogger(__name__)


class PromptProcessor:
    """Processes and enhances user prompts"""
    
    # Keywords for categorizing prompts
    CATEGORIES = {
        'modeling': [
            'create', 'model', 'mesh', 'object', 'shape', 'geometry',
            'cube', 'sphere', 'cylinder', 'cone', 'torus', 'plane',
            'extrude', 'subdivide', 'modifier', 'boolean', 'array',
            'character', 'building', 'furniture', 'vehicle'
        ],
        'material': [
            'material', 'shader', 'texture', 'color', 'metallic',
            'roughness', 'glossy', 'diffuse', 'bsdf', 'principled',
            'procedural', 'node', 'glass', 'metal', 'wood', 'stone'
        ],
        'scene': [
            'scene', 'lighting', 'light', 'camera', 'environment',
            'world', 'hdri', 'background', 'sun', 'lamp', 'composition',
            'render', 'setup', 'studio'
        ],
        'animation': [
            'animate', 'animation', 'keyframe', 'motion', 'movement',
            'rotate', 'translate', 'scale', 'path', 'timeline',
            'bounce', 'spin', 'move', 'frame'
        ]
    }
    
    # Common measurement units and their conversions
    UNITS = {
        'cm': 0.01,
        'centimeter': 0.01,
        'mm': 0.001,
        'millimeter': 0.001,
        'm': 1.0,
        'meter': 1.0,
        'inch': 0.0254,
        'inches': 0.0254,
        'ft': 0.3048,
        'foot': 0.3048,
        'feet': 0.3048,
    }
    
    def __init__(self):
        """Initialize Prompt Processor"""
        logger.info("Initialized Prompt Processor")
    
    def process(self, prompt: str) -> Dict[str, any]:
        """
        Process and analyze a user prompt
        
        Args:
            prompt (str): User's natural language prompt
            
        Returns:
            dict: Processed prompt information
        """
        # Clean and normalize prompt
        cleaned_prompt = self._clean_prompt(prompt)
        
        # Categorize prompt
        category = self._categorize_prompt(cleaned_prompt)
        
        # Extract entities (objects, materials, etc.)
        entities = self._extract_entities(cleaned_prompt)
        
        # Extract numerical values and units
        measurements = self._extract_measurements(cleaned_prompt)
        
        # Detect complexity
        complexity = self._assess_complexity(cleaned_prompt, entities)
        
        # Generate enhanced prompt
        enhanced_prompt = self._enhance_prompt(
            cleaned_prompt,
            category,
            measurements
        )
        
        result = {
            'original': prompt,
            'cleaned': cleaned_prompt,
            'enhanced': enhanced_prompt,
            'category': category,
            'entities': entities,
            'measurements': measurements,
            'complexity': complexity,
            'prompt_type': self._get_prompt_type(category)
        }
        
        logger.info(f"Processed prompt - Category: {category}, Complexity: {complexity}")
        logger.debug(f"Entities found: {entities}")
        
        return result
    
    def _clean_prompt(self, prompt: str) -> str:
        """
        Clean and normalize prompt text
        
        Args:
            prompt (str): Raw user prompt
            
        Returns:
            str: Cleaned prompt
        """
        # Remove extra whitespace
        cleaned = ' '.join(prompt.split())
        
        # Remove special characters at start/end
        cleaned = cleaned.strip('.,!?;:')
        
        # Normalize common abbreviations
        replacements = {
            "pls": "please",
            "plz": "please",
            "thx": "thanks",
            "w/": "with",
            "w/o": "without",
        }
        
        for old, new in replacements.items():
            cleaned = re.sub(r'\b' + old + r'\b', new, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _categorize_prompt(self, prompt: str) -> str:
        """
        Categorize prompt based on keywords
        
        Args:
            prompt (str): Cleaned prompt
            
        Returns:
            str: Category name ('modeling', 'material', 'scene', 'animation', 'mixed')
        """
        prompt_lower = prompt.lower()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[category] = score
        
        # Get category with highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            return 'modeling'  # Default to modeling
        
        # Check if it's mixed (multiple high scores)
        high_scoring = [cat for cat, score in scores.items() if score >= max_score * 0.7]
        
        if len(high_scoring) > 1:
            return 'mixed'
        
        return max(scores, key=scores.get)
    
    def _extract_entities(self, prompt: str) -> Dict[str, List[str]]:
        """
        Extract entities (objects, materials, colors, etc.) from prompt
        
        Args:
            prompt (str): Cleaned prompt
            
        Returns:
            dict: Dictionary of entity types and their values
        """
        entities = {
            'objects': [],
            'colors': [],
            'materials': [],
            'quantities': []
        }
        
        # Common objects
        objects = ['cube', 'sphere', 'cylinder', 'cone', 'torus', 'plane',
                  'tree', 'house', 'car', 'chair', 'table', 'lamp']
        for obj in objects:
            if re.search(r'\b' + obj + r's?\b', prompt, re.IGNORECASE):
                entities['objects'].append(obj)
        
        # Colors
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple',
                 'black', 'white', 'gray', 'grey', 'brown', 'pink']
        for color in colors:
            if re.search(r'\b' + color + r'\b', prompt, re.IGNORECASE):
                entities['colors'].append(color)
        
        # Materials
        materials = ['metal', 'wood', 'glass', 'plastic', 'stone',
                    'gold', 'silver', 'copper', 'steel', 'concrete']
        for material in materials:
            if re.search(r'\b' + material + r'\b', prompt, re.IGNORECASE):
                entities['materials'].append(material)
        
        # Extract quantities (numbers)
        quantities = re.findall(r'\b(\d+)\s+(\w+)', prompt)
        entities['quantities'] = [(int(num), obj) for num, obj in quantities]
        
        return entities
    
    def _extract_measurements(self, prompt: str) -> List[Dict[str, any]]:
        """
        Extract numerical measurements and convert to Blender units
        
        Args:
            prompt (str): Cleaned prompt
            
        Returns:
            list: List of measurement dictionaries
        """
        measurements = []
        
        # Pattern: number + unit (e.g., "5 meters", "10cm", "2.5 feet")
        pattern = r'(\d+\.?\d*)\s*(' + '|'.join(self.UNITS.keys()) + r')'
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        
        for value, unit in matches:
            blender_value = float(value) * self.UNITS.get(unit.lower(), 1.0)
            measurements.append({
                'original_value': float(value),
                'original_unit': unit,
                'blender_value': blender_value,
                'blender_unit': 'meters'
            })
        
        return measurements
    
    def _assess_complexity(self, prompt: str, entities: Dict) -> str:
        """
        Assess prompt complexity
        
        Args:
            prompt (str): Cleaned prompt
            entities (dict): Extracted entities
            
        Returns:
            str: Complexity level ('simple', 'medium', 'complex')
        """
        # Calculate complexity score
        score = 0
        
        # Word count
        word_count = len(prompt.split())
        if word_count > 50:
            score += 3
        elif word_count > 20:
            score += 2
        else:
            score += 1
        
        # Number of entities
        total_entities = sum(len(v) if isinstance(v, list) else 0
                           for v in entities.values())
        if total_entities > 10:
            score += 3
        elif total_entities > 5:
            score += 2
        else:
            score += 1
        
        # Specific complexity indicators
        complex_keywords = ['procedural', 'animation', 'rigging', 'physics',
                          'particle', 'advanced', 'realistic', 'detailed']
        if any(keyword in prompt.lower() for keyword in complex_keywords):
            score += 2
        
        # Categorize complexity
        if score <= 3:
            return 'simple'
        elif score <= 6:
            return 'medium'
        else:
            return 'complex'
    
    def _enhance_prompt(
        self,
        prompt: str,
        category: str,
        measurements: List[Dict]
    ) -> str:
        """
        Enhance prompt with additional context
        
        Args:
            prompt (str): Cleaned prompt
            category (str): Prompt category
            measurements (list): Extracted measurements
            
        Returns:
            str: Enhanced prompt
        """
        enhanced = prompt
        
        # Add category-specific guidance
        if category == 'modeling' and 'scale' not in prompt.lower():
            enhanced += " Use realistic proportions and scales."
        
        if category == 'material' and 'node' not in prompt.lower():
            enhanced += " Use node-based materials with Principled BSDF."
        
        if category == 'scene' and 'camera' not in prompt.lower():
            enhanced += " Set up appropriate camera positioning."
        
        # Add unit conversions if needed
        if measurements:
            enhanced += " (Note: measurements converted to Blender units)"
        
        return enhanced
    
    def _get_prompt_type(self, category: str) -> str:
        """
        Get the prompt file type to use
        
        Args:
            category (str): Prompt category
            
        Returns:
            str: Prompt type for file selection
        """
        type_mapping = {
            'modeling': 'modeling',
            'material': 'material',
            'scene': 'scene',
            'animation': 'animation',
            'mixed': 'base'
        }
        
        return type_mapping.get(category, 'base')
    
    def suggest_improvements(self, prompt: str) -> List[str]:
        """
        Suggest improvements to make the prompt more effective
        
        Args:
            prompt (str): User prompt
            
        Returns:
            list: List of suggestions
        """
        suggestions = []
        
        prompt_lower = prompt.lower()
        
        # Check for vagueness
        vague_words = ['thing', 'stuff', 'something', 'nice', 'good', 'cool']
        if any(word in prompt_lower for word in vague_words):
            suggestions.append("Be more specific about what you want to create")
        
        # Check for missing details
        if len(prompt.split()) < 5:
            suggestions.append("Add more details about size, color, or placement")
        
        # Check for measurements
        if any(word in prompt_lower for word in ['big', 'small', 'large', 'tiny']):
            if not re.search(r'\d+', prompt):
                suggestions.append("Specify exact measurements instead of relative sizes")
        
        # Check for materials/colors
        has_object = any(word in prompt_lower for word in ['cube', 'sphere', 'object'])
        has_color = any(word in prompt_lower for word in ['red', 'blue', 'color', 'material'])
        if has_object and not has_color:
            suggestions.append("Consider specifying colors or materials")
        
        return suggestions


def process_prompt(prompt: str) -> Dict[str, any]:
    """
    Convenience function to process a prompt
    
    Args:
        prompt (str): User prompt
        
    Returns:
        dict: Processed prompt information
    """
    processor = PromptProcessor()
    return processor.process(prompt)