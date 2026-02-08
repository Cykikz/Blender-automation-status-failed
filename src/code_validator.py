import ast
import logging
import re
from typing import Tuple, List, Optional

from config import Config

logger = logging.getLogger(__name__)


class CodeValidator:
    """Validates Blender Python code before execution"""
    
    # Dangerous operations that should be blocked
    DANGEROUS_IMPORTS = [
        'os.system',
        'subprocess',
        'eval',
        'exec',
        '__import__',
        'compile',
        'open',  # File operations can be dangerous
    ]
    
    # Required imports for Blender scripts
    REQUIRED_IMPORTS = ['bpy']
    
    # Common Blender API patterns
    RECOMMENDED_PATTERNS = [
        'bpy.ops.object.select_all',  # Clearing scene
        'bpy.data.',  # Data access
        'bpy.context.',  # Context access
    ]
    
    def __init__(self):
        """Initialize Code Validator"""
        logger.info("Initialized Code Validator")
    
    def validate(self, code: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate Python code
        
        Args:
            code (str): Python code to validate
            
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # 1. Check syntax
        syntax_valid, syntax_errors = self._check_syntax(code)
        if not syntax_valid:
            errors.extend(syntax_errors)
            return False, errors, warnings
        
        # 2. Check for dangerous operations
        security_valid, security_issues = self._check_security(code)
        if not security_valid:
            errors.extend(security_issues)
        
        # 3. Check for required imports
        import_warnings = self._check_imports(code)
        warnings.extend(import_warnings)
        
        # 4. Check Blender API usage
        api_warnings = self._check_blender_api(code)
        warnings.extend(api_warnings)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✓ Code validation passed")
        else:
            logger.error(f"✗ Code validation failed with {len(errors)} errors")
        
        if warnings:
            logger.warning(f"Code has {len(warnings)} warnings")
        
        return is_valid, errors, warnings
    
    def _check_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """
        Check Python syntax
        
        Args:
            code (str): Python code
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            error_msg = f"Syntax Error at line {e.lineno}: {e.msg}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Parsing Error: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def _check_security(self, code: str) -> Tuple[bool, List[str]]:
        """
        Check for dangerous operations
        
        Args:
            code (str): Python code
            
        Returns:
            Tuple[bool, List[str]]: (is_safe, security_issues)
        """
        issues = []
        
        # Check for dangerous imports
        for dangerous in self.DANGEROUS_IMPORTS:
            if dangerous in code:
                issues.append(f"Dangerous operation detected: {dangerous}")
        
        # Check for file operations
        file_ops = ['open(', 'write(', 'read(', 'remove(', 'unlink(']
        for op in file_ops:
            if op in code:
                # Allow only if it's part of a comment
                if not self._is_in_comment(code, op):
                    issues.append(f"File operation detected: {op}")
        
        # Check for network operations
        network_ops = ['urllib', 'requests', 'socket', 'http']
        for op in network_ops:
            if f"import {op}" in code or f"from {op}" in code:
                issues.append(f"Network operation detected: {op}")
        
        is_safe = len(issues) == 0
        
        if not is_safe:
            logger.warning(f"Security issues found: {issues}")
        
        return is_safe, issues
    
    def _check_imports(self, code: str) -> List[str]:
        """
        Check for required imports
        
        Args:
            code (str): Python code
            
        Returns:
            List[str]: Warning messages
        """
        warnings = []
        
        # Check for required imports
        for required in self.REQUIRED_IMPORTS:
            if f"import {required}" not in code and f"from {required}" not in code:
                warnings.append(f"Missing recommended import: {required}")
        
        # Check for common useful imports
        if 'math' in code.lower() and 'import math' not in code:
            warnings.append("Code mentions 'math' but doesn't import math module")
        
        if 'vector' in code.lower() and 'from mathutils import' not in code:
            warnings.append("Code mentions 'vector' but doesn't import from mathutils")
        
        return warnings
    
    def _check_blender_api(self, code: str) -> List[str]:
        """
        Check Blender API usage for best practices
        
        Args:
            code (str): Python code
            
        Returns:
            List[str]: Warning messages
        """
        warnings = []
        
        # Check if scene is cleared
        if not any(pattern in code for pattern in ['bpy.ops.object.select_all', 'bpy.ops.object.delete']):
            warnings.append("Code doesn't clear existing objects - may cause conflicts")
        
        # Check for object naming
        if 'bpy.ops.mesh' in code or 'bpy.ops.curve' in code:
            if '.name =' not in code and 'name=' not in code:
                warnings.append("Objects created but not named - may be hard to reference")
        
        # Check for proper context usage
        if 'bpy.ops.' in code and 'bpy.context.view_layer.objects.active' not in code:
            if code.count('bpy.ops.') > 5:
                warnings.append("Many operations without setting active object - may cause issues")
        
        # Check for common mistakes
        if 'bpy.data.objects.new' in code:
            if 'scene.collection.objects.link' not in code and 'bpy.context.collection.objects.link' not in code:
                warnings.append("Objects created but not linked to scene collection")
        
        return warnings
    
    def _is_in_comment(self, code: str, pattern: str) -> bool:
        """
        Check if a pattern appears only in comments
        
        Args:
            code (str): Python code
            pattern (str): Pattern to search for
            
        Returns:
            bool: True if pattern only appears in comments
        """
        for line in code.split('\n'):
            if pattern in line:
                # Check if it's after a # (comment)
                if '#' not in line or line.index(pattern) < line.index('#'):
                    return False
        return True
    
    def get_suggestions(self, code: str) -> List[str]:
        """
        Get improvement suggestions for the code
        
        Args:
            code (str): Python code
            
        Returns:
            List[str]: Suggestion messages
        """
        suggestions = []
        
        # Suggest adding error handling
        if 'try:' not in code:
            suggestions.append("Consider adding try-except blocks for error handling")
        
        # Suggest adding comments
        comment_ratio = code.count('#') / max(code.count('\n'), 1)
        if comment_ratio < 0.1:
            suggestions.append("Consider adding more comments to explain the code")
        
        # Suggest organizing with functions
        if code.count('\n') > 50 and 'def ' not in code:
            suggestions.append("Consider organizing code into functions for better readability")
        
        # Suggest using collections
        if code.count('bpy.ops.') > 10:
            if 'bpy.data.collections' not in code:
                suggestions.append("Consider using collections to organize many objects")
        
        return suggestions
    
    def auto_fix(self, code: str) -> str:
        """
        Attempt to automatically fix common issues
        
        Args:
            code (str): Python code
            
        Returns:
            str: Fixed code
        """
        fixed_code = code
        
        # Add import bpy if missing
        if 'import bpy' not in fixed_code and 'from bpy' not in fixed_code:
            fixed_code = 'import bpy\n' + fixed_code
        
        # Add scene clearing if missing
        if 'bpy.ops.object.select_all' not in fixed_code:
            clear_code = """# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

"""
            # Add after imports
            lines = fixed_code.split('\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_end = i + 1
            
            lines.insert(import_end, clear_code)
            fixed_code = '\n'.join(lines)
        
        logger.info("Applied auto-fixes to code")
        return fixed_code


def validate_code(code: str) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate code
    
    Args:
        code (str): Python code to validate
        
    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
    """
    validator = CodeValidator()
    return validator.validate(code)