import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""
    
    # ==========================================
    # PROJECT PATHS
    # ==========================================
    BASE_DIR = Path(__file__).parent.parent.resolve()
    SRC_DIR = BASE_DIR / "src"
    PROMPTS_DIR = BASE_DIR / "prompts"
    TEMPLATES_DIR = BASE_DIR / "templates"
    GENERATED_DIR = BASE_DIR / "generated"
    ARCHIVE_DIR = GENERATED_DIR / "archive"
    OUTPUT_DIR = BASE_DIR / "output"
    RENDERS_DIR = OUTPUT_DIR / "renders"
    MODELS_DIR = OUTPUT_DIR / "models"
    BLEND_FILES_DIR = OUTPUT_DIR / "blend_files"
    LOGS_DIR = BASE_DIR / "logs"
    TESTS_DIR = BASE_DIR / "tests"
    EXAMPLES_DIR = BASE_DIR / "examples"
    
    # ==========================================
    # API CONFIGURATION
    # ==========================================
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "claude").lower()
    
    # Model settings
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "codellama")
    LOCAL_LLM_TEMPERATURE = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.4"))
    LOCAL_LLM_MAX_TOKENS = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "4000"))
    LOCAL_LLM_CONTEXT_SIZE = int(os.getenv("LOCAL_LLM_CONTEXT_SIZE", "8192"))
    LOCAL_LLM_GPU_LAYERS = int(os.getenv("LOCAL_LLM_GPU_LAYERS", "-1"))
    LOCAL_LLM_BATCH_SIZE = int(os.getenv("LOCAL_LLM_BATCH_SIZE", "512"))
    LOCAL_LLM_USE_MMAP = os.getenv("LOCAL_LLM_USE_MMAP", "true").lower() == "true"
    LOCAL_LLM_NUM_THREADS = int(os.getenv("LOCAL_LLM_NUM_THREADS", "0"))
    
    # ==========================================
    # BLENDER CONFIGURATION
    # ==========================================
    BLENDER_PATH = os.getenv("BLENDER_PATH", "blender")
    DEFAULT_MODE = os.getenv("DEFAULT_MODE", "background")
    
    # ==========================================
    # OUTPUT SETTINGS
    # ==========================================
    AUTO_RENDER = os.getenv("AUTO_RENDER", "false").lower() == "true"
    AUTO_SAVE = os.getenv("AUTO_SAVE", "true").lower() == "true"
    AUTO_EXPORT = os.getenv("AUTO_EXPORT", "false").lower() == "true"
    EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "obj").lower()
    
    # Render settings
    RENDER_WIDTH = int(os.getenv("RENDER_WIDTH", "1920"))
    RENDER_HEIGHT = int(os.getenv("RENDER_HEIGHT", "1080"))
    RENDER_SAMPLES = int(os.getenv("RENDER_SAMPLES", "128"))
    RENDER_ENGINE = os.getenv("RENDER_ENGINE", "CYCLES")
    
    # ==========================================
    # LOGGING SETTINGS
    # ==========================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "logs/blender_ai.log")
    
    # ==========================================
    # ADVANCED SETTINGS
    # ==========================================
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    VALIDATE_CODE = os.getenv("VALIDATE_CODE", "true").lower() == "true"
    SAVE_FAILED_CODE = os.getenv("SAVE_FAILED_CODE", "true").lower() == "true"
    ARCHIVE_GENERATIONS = os.getenv("ARCHIVE_GENERATIONS", "true").lower() == "true"
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls):
        """
        Validate configuration and check for required settings
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If critical configuration is missing
        """
        errors = []
        
        # Check API keys based on provider
        if cls.AI_PROVIDER == "claude":
            if not cls.ANTHROPIC_API_KEY:
                errors.append("ANTHROPIC_API_KEY is required when AI_PROVIDER=claude")
        
        if cls.AI_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                errors.append("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        
        if cls.AI_PROVIDER == "local":
            # Validate local LLM URL is accessible (optional check)
            pass
        
        if cls.AI_PROVIDER not in ["claude", "openai", "local"]:
            errors.append(f"Invalid AI_PROVIDER: {cls.AI_PROVIDER}. Must be 'claude', 'openai', or 'local'")
        
        # Check Blender path
        if cls.BLENDER_PATH != "blender":
            blender_path = Path(cls.BLENDER_PATH)
            if not blender_path.exists():
                errors.append(f"Blender not found at: {cls.BLENDER_PATH}")
        
        # Check mode
        if cls.DEFAULT_MODE not in ["background", "gui"]:
            errors.append(f"Invalid DEFAULT_MODE: {cls.DEFAULT_MODE}. Must be 'background' or 'gui'")
        
        # Validate export format
        valid_formats = ["obj", "fbx", "gltf", "stl", "ply"]
        if cls.EXPORT_FORMAT not in valid_formats:
            errors.append(f"Invalid EXPORT_FORMAT: {cls.EXPORT_FORMAT}. Must be one of {valid_formats}")
        
        # Validate render engine
        if cls.RENDER_ENGINE not in ["CYCLES", "EEVEE"]:
            errors.append(f"Invalid RENDER_ENGINE: {cls.RENDER_ENGINE}. Must be 'CYCLES' or 'EEVEE'")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_msg)
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Create all necessary directories if they don't exist"""
        directories = [
            cls.GENERATED_DIR,
            cls.ARCHIVE_DIR,
            cls.RENDERS_DIR,
            cls.MODELS_DIR,
            cls.BLEND_FILES_DIR,
            cls.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def setup_logging(cls):
        """Set up logging configuration"""
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)
        
        # Create logs directory
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
        
        # File handler
        if cls.LOG_TO_FILE:
            file_handler = logging.FileHandler(cls.LOG_FILE)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=handlers
        )
    
    @classmethod
    def initialize(cls):
        """Initialize configuration - call this at startup"""
        try:
            cls.validate()
            cls.create_directories()
            cls.setup_logging()
            
            logger = logging.getLogger(__name__)
            logger.info("Configuration initialized successfully")
            logger.info(f"AI Provider: {cls.AI_PROVIDER}")
            logger.info(f"Blender Path: {cls.BLENDER_PATH}")
            logger.info(f"Default Mode: {cls.DEFAULT_MODE}")
            
            return True
            
        except ValueError as e:
            print(f"❌ Configuration Error: {e}")
            print("\n💡 Please check your .env file and make sure all required settings are configured.")
            return False
    
    @classmethod
    def get_prompt_file(cls, prompt_type):
        """
        Get the path to a specific prompt file
        
        Args:
            prompt_type (str): Type of prompt (base, modeling, material, scene, animation)
            
        Returns:
            Path: Path to the prompt file
        """
        prompt_files = {
            "base": cls.PROMPTS_DIR / "base_system_prompt.txt",
            "modeling": cls.PROMPTS_DIR / "modeling_expert.txt",
            "material": cls.PROMPTS_DIR / "material_expert.txt",
            "scene": cls.PROMPTS_DIR / "scene_expert.txt",
            "animation": cls.PROMPTS_DIR / "animation_expert.txt",
        }
        
        return prompt_files.get(prompt_type, prompt_files["base"])


# Initialize configuration on import
if __name__ != "__main__":
    Config.initialize()