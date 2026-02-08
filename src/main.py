"""
Blender AI Automation - Main Entry Point

This is the main application that orchestrates the entire workflow:
1. Process user prompt
2. Generate Blender Python code using AI
3. Validate the code
4. Execute in Blender
5. Handle output (render, export, save)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from prompt_processor import PromptProcessor
from ai_generator import AIGenerator
from code_validator import CodeValidator
from blender_executor import BlenderExecutor

logger = logging.getLogger(__name__)


class BlenderAI:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        # Initialize configuration
        if not Config.initialize():
            raise RuntimeError("Failed to initialize configuration")
        
        # Initialize components
        self.prompt_processor = PromptProcessor()
        self.ai_generator = AIGenerator()
        self.code_validator = CodeValidator()
        self.blender_executor = BlenderExecutor()
        
        logger.info("Blender AI Automation initialized successfully")
    
    def run(
        self,
        prompt: str,
        mode: Optional[str] = None,
        render: Optional[bool] = None,
        export: Optional[bool] = None,
        save: Optional[bool] = None,
        validate: Optional[bool] = None,
        max_retries: Optional[int] = None
    ) -> dict:
        """
        Main execution flow
        
        Args:
            prompt (str): User's natural language prompt
            mode (str, optional): Execution mode ('background' or 'gui')
            render (bool, optional): Whether to render output
            export (bool, optional): Whether to export model
            save (bool, optional): Whether to save .blend file
            validate (bool, optional): Whether to validate code
            max_retries (int, optional): Maximum regeneration attempts
            
        Returns:
            dict: Execution results
        """
        # Use config defaults if not specified
        validate = validate if validate is not None else Config.VALIDATE_CODE
        max_retries = max_retries or Config.MAX_RETRIES
        
        logger.info(f"Processing prompt: {prompt}")
        print("\n" + "="*60)
        print("BLENDER AI AUTOMATION")
        print("="*60)
        print(f"\n📝 Your prompt: {prompt}\n")
        
        # Step 1: Process prompt
        print("🔍 Processing prompt...")
        processed = self.prompt_processor.process(prompt)
        print(f"   Category: {processed['category']}")
        print(f"   Complexity: {processed['complexity']}")
        
        if processed['entities']['objects']:
            print(f"   Objects detected: {', '.join(processed['entities']['objects'])}")
        
        # Step 2: Generate code
        print("\n🤖 Generating Blender code with AI...")
        
        attempt = 0
        code = None
        is_valid = False
        
        while attempt < max_retries:
            attempt += 1
            
            if attempt > 1:
                print(f"   Retry attempt {attempt}/{max_retries}...")
            
            try:
                code = self.ai_generator.generate_code(
                    processed['enhanced'],
                    prompt_type=processed['prompt_type']
                )
                
                # Step 3: Validate code
                if validate:
                    print("\n✅ Validating generated code...")
                    is_valid, errors, warnings = self.code_validator.validate(code)
                    
                    if errors:
                        print(f"   ❌ Validation errors:")
                        for error in errors:
                            print(f"      - {error}")
                        
                        if attempt < max_retries:
                            continue
                    
                    if warnings:
                        print(f"   ⚠️  Warnings:")
                        for warning in warnings[:3]:  # Show first 3 warnings
                            print(f"      - {warning}")
                    
                    if is_valid:
                        print("   ✓ Code validation passed")
                        break
                else:
                    is_valid = True
                    break
                    
            except Exception as e:
                logger.error(f"Code generation failed: {e}")
                if attempt >= max_retries:
                    print(f"\n❌ Failed to generate valid code after {max_retries} attempts")
                    return {'success': False, 'error': str(e)}
        
        if not code:
            return {'success': False, 'error': 'Failed to generate code'}
        
        # Step 4: Save generated code
        print("\n💾 Saving generated code...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = f"generated_{timestamp}.py"
        script_path = Config.GENERATED_DIR / script_name
        
        with open(script_path, 'w') as f:
            f.write(code)
        
        print(f"   Saved to: {script_path}")
        
        # Display code preview
        print("\n📄 Generated Code Preview:")
        print("-" * 60)
        lines = code.split('\n')
        preview_lines = min(15, len(lines))
        for line in lines[:preview_lines]:
            print(f"   {line}")
        if len(lines) > preview_lines:
            print(f"   ... ({len(lines) - preview_lines} more lines)")
        print("-" * 60)
        
        # Step 5: Execute in Blender
        print(f"\n🎨 Executing in Blender ({mode or Config.DEFAULT_MODE} mode)...")
        
        try:
            results = self.blender_executor.execute_full_pipeline(
                script_path,
                mode=mode,
                render=render,
                export=export,
                save=save
            )
            
            if results['success']:
                print("\n✅ SUCCESS! Blender execution completed\n")
                
                # Show output paths
                if results.get('render_path'):
                    print(f"   🖼️  Render: {results['render_path']}")
                if results.get('export_path'):
                    print(f"   📦 Export: {results['export_path']}")
                if results.get('blend_path'):
                    print(f"   💾 Blend file: {results['blend_path']}")
                
                print(f"\n   📁 Generated script: {script_path}")
                
            else:
                print("\n❌ Execution failed")
                print("\nBlender output:")
                print(results['stderr'][:500])  # Show first 500 chars of error
                
                # Save failed code if configured
                if Config.SAVE_FAILED_CODE:
                    failed_path = Config.GENERATED_DIR / f"failed_{timestamp}.py"
                    with open(failed_path, 'w') as f:
                        f.write(code)
                    print(f"\n   Failed code saved to: {failed_path}")
            
            # Archive if configured
            if Config.ARCHIVE_GENERATIONS and results['success']:
                self._archive_generation(script_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            print(f"\n❌ Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _archive_generation(self, script_path: Path):
        """Archive a successful generation"""
        try:
            archive_path = Config.ARCHIVE_DIR / script_path.name
            with open(script_path, 'r') as src, open(archive_path, 'w') as dst:
                dst.write(src.read())
            logger.debug(f"Archived generation to {archive_path}")
        except Exception as e:
            logger.warning(f"Failed to archive generation: {e}")
    
    def interactive_mode(self):
        """Run in interactive mode with user input loop"""
        print("\n" + "="*60)
        print("BLENDER AI AUTOMATION - Interactive Mode")
        print("="*60)
        print("\nEnter your prompts to generate Blender scenes.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        while True:
            try:
                prompt = input("🎨 Describe what you want to create:\n> ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not prompt:
                    continue
                
                # Run generation
                results = self.run(prompt)
                
                # Ask if user wants to refine
                if results.get('success'):
                    refine = input("\n🔄 Would you like to refine this? (y/n): ").strip().lower()
                    if refine == 'y':
                        feedback = input("What changes would you like? ").strip()
                        if feedback:
                            # TODO: Implement refinement
                            print("Refinement feature coming soon!")
                
                print("\n" + "-"*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point with command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Generate Blender 3D scenes from natural language prompts using AI"
    )
    
    parser.add_argument(
        'prompt',
        nargs='*',
        help='Description of what to create in Blender'
    )
    
    parser.add_argument(
        '--mode',
        choices=['background', 'gui'],
        help='Execution mode (default: from config)'
    )
    
    parser.add_argument(
        '--render',
        action='store_true',
        help='Render the scene to an image'
    )
    
    parser.add_argument(
        '--no-render',
        action='store_true',
        help='Do not render (override config)'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export the model'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save as .blend file'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip code validation'
    )
    
    parser.add_argument(
        '--interactive',
        '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--provider',
        choices=['claude', 'openai', 'local'],
        help='AI provider to use'
    )
    
    args = parser.parse_args()
    
    try:
        # Override config with command-line args
        if args.provider:
            Config.AI_PROVIDER = args.provider
        
        # Initialize application
        app = BlenderAI()
        
        # Run in appropriate mode
        if args.interactive or not args.prompt:
            app.interactive_mode()
        else:
            # Join prompt words
            prompt = ' '.join(args.prompt)
            
            # Determine render setting
            render = None
            if args.render:
                render = True
            elif args.no_render:
                render = False
            
            # Run generation
            results = app.run(
                prompt,
                mode=args.mode,
                render=render,
                export=args.export,
                save=args.save,
                validate=not args.no_validate
            )
            
            # Exit with appropriate code
            sys.exit(0 if results.get('success') else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()