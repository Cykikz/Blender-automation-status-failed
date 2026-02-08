import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)


class BlenderExecutor:
    """Executes Python scripts in Blender"""
    
    def __init__(self, blender_path: Optional[str] = None):
        """
        Initialize Blender Executor
        
        Args:
            blender_path (str, optional): Path to Blender executable
        """
        self.blender_path = blender_path or Config.BLENDER_PATH
        
        # Verify Blender is accessible
        if not self._verify_blender():
            raise ValueError(f"Blender not found or not executable at: {self.blender_path}")
        
        logger.info(f"Initialized Blender Executor with: {self.blender_path}")
    
    def _verify_blender(self) -> bool:
        """
        Verify that Blender is accessible
        
        Returns:
            bool: True if Blender can be executed
        """
        try:
            result = subprocess.run(
                [self.blender_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                logger.info(f"Found {version_info}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to verify Blender: {e}")
            return False
    
    def execute_script(
        self,
        script_path: Path,
        mode: Optional[str] = None,
        timeout: int = 300
    ) -> Tuple[bool, str, str]:
        """
        Execute a Python script in Blender
        
        Args:
            script_path (Path): Path to the Python script
            mode (str, optional): Execution mode ('background' or 'gui')
            timeout (int): Maximum execution time in seconds
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        mode = mode or Config.DEFAULT_MODE
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Build command
        cmd = [self.blender_path]
        
        if mode == "background":
            cmd.append("--background")
        
        cmd.extend(["--python", str(script_path)])
        
        logger.info(f"Executing script in {mode} mode: {script_path.name}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Config.BASE_DIR
            )
            
            success = result.returncode == 0
            
            if success:
                logger.info(f"✓ Script executed successfully")
            else:
                logger.error(f"✗ Script execution failed with code {result.returncode}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script execution timed out after {timeout} seconds")
            return False, "", "Execution timed out"
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            return False, "", str(e)
    
    def execute_with_render(
        self,
        script_path: Path,
        output_path: Optional[Path] = None,
        mode: str = "background"
    ) -> Tuple[bool, str, str]:
        """
        Execute script and render the result
        
        Args:
            script_path (Path): Path to the Python script
            output_path (Path, optional): Path for rendered image
            mode (str): Execution mode
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Config.RENDERS_DIR / f"render_{timestamp}.png"
        
        # Create a combined script that includes rendering
        render_script = self._create_render_script(script_path, output_path)
        
        logger.info(f"Executing with render output to: {output_path}")
        
        return self.execute_script(render_script, mode=mode)
    
    def execute_with_export(
        self,
        script_path: Path,
        export_path: Optional[Path] = None,
        export_format: Optional[str] = None,
        mode: str = "background"
    ) -> Tuple[bool, str, str]:
        """
        Execute script and export the model
        
        Args:
            script_path (Path): Path to the Python script
            export_path (Path, optional): Path for exported model
            export_format (str, optional): Export format ('obj', 'fbx', 'gltf', etc.)
            mode (str): Execution mode
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        export_format = export_format or Config.EXPORT_FORMAT
        
        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Config.MODELS_DIR / f"model_{timestamp}.{export_format}"
        
        # Create a combined script that includes exporting
        export_script = self._create_export_script(script_path, export_path, export_format)
        
        logger.info(f"Executing with {export_format.upper()} export to: {export_path}")
        
        return self.execute_script(export_script, mode=mode)
    
    def execute_with_save(
        self,
        script_path: Path,
        blend_path: Optional[Path] = None,
        mode: str = "background"
    ) -> Tuple[bool, str, str]:
        """
        Execute script and save the .blend file
        
        Args:
            script_path (Path): Path to the Python script
            blend_path (Path, optional): Path for .blend file
            mode (str): Execution mode
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        if blend_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blend_path = Config.BLEND_FILES_DIR / f"scene_{timestamp}.blend"
        
        # Create a combined script that includes saving
        save_script = self._create_save_script(script_path, blend_path)
        
        logger.info(f"Executing with save to: {blend_path}")
        
        return self.execute_script(save_script, mode=mode)
    
    def _create_render_script(self, script_path: Path, output_path: Path) -> Path:
        """Create a temporary script that includes rendering"""
        with open(script_path, 'r') as f:
            original_code = f.read()
        
        render_code = f"""
# Render configuration
import bpy

bpy.context.scene.render.filepath = r"{output_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_x = {Config.RENDER_WIDTH}
bpy.context.scene.render.resolution_y = {Config.RENDER_HEIGHT}
bpy.context.scene.render.engine = '{Config.RENDER_ENGINE}'

if bpy.context.scene.render.engine == 'CYCLES':
    bpy.context.scene.cycles.samples = {Config.RENDER_SAMPLES}

# Render
bpy.ops.render.render(write_still=True)
print(f"Rendered to: {output_path}")
"""
        
        combined_script = original_code + "\n\n" + render_code
        
        temp_script = Config.GENERATED_DIR / f"temp_render_{script_path.stem}.py"
        with open(temp_script, 'w') as f:
            f.write(combined_script)
        
        return temp_script
    
    def _create_export_script(
        self,
        script_path: Path,
        export_path: Path,
        export_format: str
    ) -> Path:
        """Create a temporary script that includes exporting"""
        with open(script_path, 'r') as f:
            original_code = f.read()
        
        # Map export formats to Blender operators
        export_ops = {
            'obj': f"bpy.ops.wm.obj_export(filepath=r'{export_path}')",
            'fbx': f"bpy.ops.export_scene.fbx(filepath=r'{export_path}')",
            'gltf': f"bpy.ops.export_scene.gltf(filepath=r'{export_path}')",
            'stl': f"bpy.ops.export_mesh.stl(filepath=r'{export_path}')",
            'ply': f"bpy.ops.export_mesh.ply(filepath=r'{export_path}')",
        }
        
        export_op = export_ops.get(export_format.lower())
        if not export_op:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        export_code = f"""
# Export model
import bpy

{export_op}
print(f"Exported to: {export_path}")
"""
        
        combined_script = original_code + "\n\n" + export_code
        
        temp_script = Config.GENERATED_DIR / f"temp_export_{script_path.stem}.py"
        with open(temp_script, 'w') as f:
            f.write(combined_script)
        
        return temp_script
    
    def _create_save_script(self, script_path: Path, blend_path: Path) -> Path:
        """Create a temporary script that includes saving"""
        with open(script_path, 'r') as f:
            original_code = f.read()
        
        save_code = f"""
# Save blend file
import bpy

bpy.ops.wm.save_as_mainfile(filepath=r"{blend_path}")
print(f"Saved to: {blend_path}")
"""
        
        combined_script = original_code + "\n\n" + save_code
        
        temp_script = Config.GENERATED_DIR / f"temp_save_{script_path.stem}.py"
        with open(temp_script, 'w') as f:
            f.write(combined_script)
        
        return temp_script
    
    def execute_full_pipeline(
        self,
        script_path: Path,
        mode: Optional[str] = None,
        render: Optional[bool] = None,
        export: Optional[bool] = None,
        save: Optional[bool] = None
    ) -> Dict[str, any]:
        """
        Execute the full pipeline based on configuration
        
        Args:
            script_path (Path): Path to the Python script
            mode (str, optional): Execution mode
            render (bool, optional): Whether to render
            export (bool, optional): Whether to export
            save (bool, optional): Whether to save .blend
            
        Returns:
            dict: Results dictionary with paths and success status
        """
        mode = mode or Config.DEFAULT_MODE
        render = render if render is not None else Config.AUTO_RENDER
        export = export if export is not None else Config.AUTO_EXPORT
        save = save if save is not None else Config.AUTO_SAVE
        
        results = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'render_path': None,
            'export_path': None,
            'blend_path': None
        }
        
        # Determine which operations to perform
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if render:
            render_path = Config.RENDERS_DIR / f"render_{timestamp}.png"
            results['render_path'] = render_path
        
        if export:
            export_path = Config.MODELS_DIR / f"model_{timestamp}.{Config.EXPORT_FORMAT}"
            results['export_path'] = export_path
        
        if save:
            blend_path = Config.BLEND_FILES_DIR / f"scene_{timestamp}.blend"
            results['blend_path'] = blend_path
        
        # Create combined script with all operations
        final_script = self._create_combined_script(
            script_path,
            results.get('render_path'),
            results.get('export_path'),
            results.get('blend_path')
        )
        
        # Execute
        success, stdout, stderr = self.execute_script(final_script, mode=mode)
        
        results['success'] = success
        results['stdout'] = stdout
        results['stderr'] = stderr
        
        return results
    
    def _create_combined_script(
        self,
        script_path: Path,
        render_path: Optional[Path],
        export_path: Optional[Path],
        blend_path: Optional[Path]
    ) -> Path:
        """Create a script with all operations combined"""
        with open(script_path, 'r') as f:
            original_code = f.read()
        
        additional_code = "\nimport bpy\n"
        
        # Add render code
        if render_path:
            additional_code += f"""
# Render
bpy.context.scene.render.filepath = r"{render_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_x = {Config.RENDER_WIDTH}
bpy.context.scene.render.resolution_y = {Config.RENDER_HEIGHT}
bpy.context.scene.render.engine = '{Config.RENDER_ENGINE}'
if bpy.context.scene.render.engine == 'CYCLES':
    bpy.context.scene.cycles.samples = {Config.RENDER_SAMPLES}
bpy.ops.render.render(write_still=True)
print(f"Rendered to: {render_path}")
"""
        
        # Add export code
        if export_path:
            export_format = Config.EXPORT_FORMAT
            export_ops = {
                'obj': f"bpy.ops.wm.obj_export(filepath=r'{export_path}')",
                'fbx': f"bpy.ops.export_scene.fbx(filepath=r'{export_path}')",
                'gltf': f"bpy.ops.export_scene.gltf(filepath=r'{export_path}')",
                'stl': f"bpy.ops.export_mesh.stl(filepath=r'{export_path}')",
            }
            additional_code += f"""
# Export
{export_ops.get(export_format)}
print(f"Exported to: {export_path}")
"""
        
        # Add save code
        if blend_path:
            additional_code += f"""
# Save
bpy.ops.wm.save_as_mainfile(filepath=r"{blend_path}")
print(f"Saved to: {blend_path}")
"""
        
        combined_script = original_code + "\n" + additional_code
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_script = Config.GENERATED_DIR / f"combined_{timestamp}.py"
        with open(final_script, 'w') as f:
            f.write(combined_script)
        
        return final_script