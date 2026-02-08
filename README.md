# Failed
## Can try and play around with it but due to current tech limitations and some problems it's not working great what it does rn --> give prompt ---> generated python script (sucks even claude can't generate good scripts rn) ----> fails to run the script / does some work but ultimately does nothing keepin it here so someone interested can use it and do something with it or maybe I'll do something in future when I can.

# AI-Powered Blender Automation

Automatically generate 3D scenes, objects, and models in Blender from natural language prompts using Claude or other LLMs.

## Overview

This system allows you to describe what you want in plain English (or other languages), and have an AI automatically generate the corresponding Blender Python scripts to create 3D models, scenes, materials, and animations.

**Example prompts:**
- "Create a low-poly forest scene with 10 pine trees"
- "Model a detailed coffee mug with a handle"
- "Generate a procedural material that looks like old copper"
- "Animate a bouncing ball with realistic physics"

## Architecture

```
User Prompt → AI (Claude/GPT) → Blender Python Script → Blender → 3D Output
```

The system works by:
1. Taking your natural language description
2. Using an LLM to generate Blender Python (bpy) code
3. Executing that code in Blender to create the 3D content
4. Optionally rendering or exporting the result

## Prerequisites

### Required Software
- **Blender** (3.0 or newer recommended): [Download here](https://www.blender.org/download/)
- **Python** (3.10+): Usually bundled with Blender, but you may need standalone Python for the automation script
- **API Access**: One of the following:
  - Anthropic API key (for Claude)
  - OpenAI API key (for ChatGPT)
  - Local LLM setup (Ollama, LM Studio, etc.)

### Python Packages
```bash
pip install anthropic  # for Claude
# OR
pip install openai     # for ChatGPT
# OR
pip install requests   # for local LLMs
```

## Setup

### 1. Get Your API Key

**For Claude (Anthropic):**
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key and copy it

**For ChatGPT (OpenAI):**
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key and copy it

### 2. Set Up Environment Variables

Create a `.env` file in your project directory:

```bash
# For Claude
ANTHROPIC_API_KEY=your_api_key_here

# For ChatGPT
OPENAI_API_KEY=your_api_key_here

# Blender path (adjust to your installation)
BLENDER_PATH=/usr/bin/blender  # Linux
# BLENDER_PATH=C:\Program Files\Blender Foundation\Blender\blender.exe  # Windows
# BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender  # macOS
```

### 3. Project Structure

```
blender-ai-automation/
├── .env                      # API keys and configuration
├── main.py                   # Main automation script
├── prompts/                  # System prompts for the AI
│   └── blender_expert.txt
├── generated/                # Generated Python scripts
│   └── .gitkeep
├── output/                   # Rendered images/models
│   └── .gitkeep
└── README.md                 # This file
```

## Implementation

### Option A: Using Claude API (Recommended)

Create `main.py`:

```python
import os
import subprocess
import anthropic
from pathlib import Path

# Load API key
API_KEY = os.getenv("ANTHROPIC_API_KEY")
BLENDER_PATH = os.getenv("BLENDER_PATH", "blender")

client = anthropic.Anthropic(api_key=API_KEY)

# System prompt to guide Claude
SYSTEM_PROMPT = """You are an expert Blender Python (bpy) developer. 
When given a description of a 3D scene or object, you generate clean, 
working Python code using the Blender Python API (bpy).

Requirements:
- Use bpy module for all Blender operations
- Clear all existing objects first: bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
- Add proper error handling
- Include comments explaining key steps
- Use realistic scales and proportions
- Return ONLY the Python code, no explanations before or after
- Code should be ready to run in Blender's Python environment

Example structure:
```python
import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Your code here
# ...
```
"""

def generate_blender_code(prompt):
    """Generate Blender Python code from natural language prompt"""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract code from response
    code = message.content[0].text
    
    # Remove markdown code blocks if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()
    
    return code

def save_and_execute(code, script_name="generated_scene.py"):
    """Save code and execute it in Blender"""
    
    # Create directories if they don't exist
    Path("generated").mkdir(exist_ok=True)
    
    # Save the generated code
    script_path = Path("generated") / script_name
    with open(script_path, "w") as f:
        f.write(code)
    
    print(f"✓ Saved script to {script_path}")
    print("\n" + "="*50)
    print("GENERATED CODE:")
    print("="*50)
    print(code)
    print("="*50 + "\n")
    
    # Execute in Blender
    print("Executing in Blender...")
    cmd = [
        BLENDER_PATH,
        "--background",  # Run without GUI
        "--python", str(script_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Successfully executed in Blender")
    else:
        print("✗ Error executing in Blender:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    print("AI-Powered Blender Automation")
    print("="*50)
    
    # Get user prompt
    prompt = input("\nDescribe what you want to create in Blender:\n> ")
    
    print("\nGenerating code...")
    code = generate_blender_code(prompt)
    
    print("\nExecuting in Blender...")
    success = save_and_execute(code)
    
    if success:
        print("\n✓ Done! Check your Blender instance or the generated files.")
    else:
        print("\n✗ There was an error. Check the output above.")

if __name__ == "__main__":
    main()
```

### Option B: Interactive Mode with GUI

For a version that opens Blender's GUI instead of running headless, modify the execution command:

```python
# In save_and_execute function, replace cmd with:
cmd = [
    BLENDER_PATH,
    "--python", str(script_path)
]
# This will open Blender GUI with your scene loaded
```

### Option C: Using Local LLM (Ollama)

If you want to run this without API costs using a local model:

```python
import requests
import json

def generate_blender_code_local(prompt):
    """Generate code using local Ollama instance"""
    
    url = "http://localhost:11434/api/generate"
    
    full_prompt = f"""{SYSTEM_PROMPT}

User request: {prompt}

Generate the Python code:"""
    
    payload = {
        "model": "codellama",  # or "deepseek-coder", "mixtral", etc.
        "prompt": full_prompt,
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    code = response.json()["response"]
    
    # Clean up code
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    
    return code
```

## Usage Examples

### Example 1: Simple Geometric Scene

**Prompt:**
```
Create a scene with a red cube, a blue sphere next to it, and a green cylinder behind them
```

**Expected Output:**
- Blender file with three objects positioned as described
- Materials with the specified colors

### Example 2: More Complex Scene

**Prompt:**
```
Create a low-poly island scene with:
- A flat plane for water (blue material)
- A raised landmass in the center
- 5 palm trees scattered around
- A sun lamp for lighting
```

### Example 3: Procedural Material

**Prompt:**
```
Create a sphere and apply a procedural material that looks like polished gold
```

### Example 4: Animation

**Prompt:**
```
Create a bouncing ball animation:
- Red sphere starting at height 5
- Bounces on a ground plane
- Animation lasts 120 frames
- Add squash and stretch
```

## Advanced Features

### 1. Render Output

Modify your script to automatically render:

```python
def render_scene(output_path="output/render.png"):
    """Render the scene to an image"""
    
    render_script = f"""
import bpy

# Set render settings
bpy.context.scene.render.filepath = "{output_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Render
bpy.ops.render.render(write_still=True)
"""
    
    # Execute after main script
    # ... combine with your generated code
```

### 2. Export Models

Add export functionality:

```python
# Add to your generated code
bpy.ops.export_scene.obj(filepath="output/model.obj")
# or
bpy.ops.export_scene.gltf(filepath="output/model.gltf")
```

### 3. Iterative Refinement

Create a loop that lets you refine the output:

```python
def iterative_mode():
    code = generate_blender_code(initial_prompt)
    
    while True:
        save_and_execute(code)
        
        feedback = input("\nWant to modify? (describe changes or 'done'): ")
        if feedback.lower() == 'done':
            break
        
        # Send both original code and feedback to AI
        refinement_prompt = f"""Here's the current code:
{code}

User wants this change: {feedback}

Provide the updated complete code:"""
        
        code = generate_blender_code(refinement_prompt)
```

### 4. Template Library

Build up a library of working examples:

```python
TEMPLATES = {
    "basic_scene": "Create a scene with a plane, cube, and camera",
    "character_base": "Create a basic humanoid mesh for character modeling",
    "environment": "Create a simple outdoor environment with terrain",
}

# User can select template + add custom modifications
```

## Tips for Better Results

### Writing Good Prompts

**Good:**
- "Create a coffee mug with a cylindrical body, a handle on the right side, and a smooth ceramic material"
- "Generate a pine tree using a cone for foliage and cylinder for trunk, make it 5 units tall"

**Less Good:**
- "Make a mug" (too vague)
- "Create the most amazing photorealistic dragon ever" (too complex for one prompt)

### Prompt Engineering Tips

1. **Be specific about dimensions**: "cube that is 2x2x2 units"
2. **Specify positions**: "sphere at coordinates (0, 0, 5)"
3. **Mention materials/colors**: "with a red metallic material"
4. **Break complex scenes into steps**: Generate parts separately, then combine
5. **Reference Blender terminology**: "use subdivision surface modifier"

## Troubleshooting

### Common Issues

**"Command 'blender' not found"**
- Set BLENDER_PATH in .env to full path to Blender executable

**"API key not found"**
- Make sure .env file exists and has correct key
- Load environment variables: `pip install python-dotenv` and add to script

**Code generates but doesn't work**
- Check Blender version compatibility
- Some features require specific Blender versions
- Try simplifying the prompt

**Blender crashes or hangs**
- Reduce complexity in prompt
- Check generated code for infinite loops
- Monitor memory usage for heavy scenes

### Debugging

Add verbose output:

```python
# In save_and_execute function
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
```

## Limitations

- Complex organic modeling (characters, creatures) may not work well
- Very specific artistic styles require fine-tuning
- Physics simulations need careful parameter specification
- The AI may not know about very new Blender features
- Large scenes may be slow to generate

## Next Steps

### Improvements You Can Add

1. **Web Interface**: Build a Flask/FastAPI web UI
2. **Version Control**: Save iterations of generations
3. **Prompt Library**: Build a database of successful prompts
4. **Multi-step Generation**: Break complex scenes into phases
5. **Style Transfer**: Apply existing Blender files as style references
6. **Batch Processing**: Generate multiple variations
7. **Quality Scoring**: Rate outputs and fine-tune prompts

### Learning Resources

- [Blender Python API Docs](https://docs.blender.org/api/current/)
- [Blender Scripting Tutorial](https://docs.blender.org/manual/en/latest/advanced/scripting/introduction.html)
- [bpy Examples](https://github.com/njanakiev/blender-scripting)

## Contributing

Feel free to extend this system! Some ideas:
- Add support for more LLM providers
- Create a prompt template system
- Build a gallery of successful generations
- Add automatic quality checking

## License

This is a personal project template. Adjust licensing as needed for your use case.

---

**Happy Creating! 🎨🤖**

For questions or issues, consult the Blender Python API documentation or adjust your prompts for better results.
