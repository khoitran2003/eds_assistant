import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find the project root directory by looking for setup.py or requirements.txt

    Args:
        start_path: Starting path for search (defaults to current directory)

    Returns:
        Path: Path to the project root directory

    Raises:
        FileNotFoundError: If project root cannot be found
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path = Path(start_path).resolve()

    # Files/folders that mark the project root
    root_markers = ["setup.py", "requirements.txt", "pyproject.toml", ".git", "main.py"]

    # Search from current directory upwards
    for parent in [current_path] + list(current_path.parents):
        for marker in root_markers:
            if (parent / marker).exists():
                return parent

    # If not found, return current directory
    return current_path


def load_env_file(
    env_filename: str = ".env",
    project_root: Optional[Path] = None,
    override: bool = True,
) -> bool:
    """
    Load .env file from project root directory

    Args:
        env_filename: Name of env file (default '.env')
        project_root: Path to project root (auto-detect if None)
        override: Whether to override existing environment variables

    Returns:
        bool: True if loaded successfully, False otherwise
    """
    try:
        if project_root is None:
            project_root = find_project_root()

        env_path = project_root / env_filename

        if not env_path.exists():
            print(f"Warning: File {env_filename} does not exist at {env_path}")
            return False

        # Load .env file
        loaded = load_dotenv(env_path, override=override)

        if loaded:
            print(f"Successfully loaded {env_filename} from {env_path}")
        else:
            print(f"Failed to load {env_filename} from {env_path}")

        return loaded

    except Exception as e:
        print(f"Error loading {env_filename}: {str(e)}")
        return False


def get_env_var(
    var_name: str,
    default: Optional[str] = None,
    required: bool = False,
    auto_load: bool = True,
) -> Optional[str]:
    """
    Get environment variable value

    Args:
        var_name: Environment variable name
        default: Default value if not found
        required: Whether this variable is required
        auto_load: Automatically load .env if not already loaded

    Returns:
        str: Environment variable value or None

    Raises:
        ValueError: If required variable is not found
    """
    # Auto-load .env if needed
    if auto_load and var_name not in os.environ:
        load_env_file()

    value = os.getenv(var_name, default)

    if required and value is None:
        raise ValueError(f"Required environment variable '{var_name}' not found")

    return value


def get_all_env_vars(
    prefix: Optional[str] = None, auto_load: bool = True
) -> Dict[str, str]:
    """
    Get all environment variables or those with specific prefix

    Args:
        prefix: Environment variable prefix (e.g., 'DB_')
        auto_load: Automatically load .env if needed

    Returns:
        Dict[str, str]: Dictionary containing environment variables
    """
    if auto_load:
        load_env_file()

    if prefix:
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

    return dict(os.environ)


def ensure_env_loaded(env_filename: str = ".env") -> None:
    """
    Ensure .env file has been loaded
    This function should be called at the beginning of modules or application

    Args:
        env_filename: Name of env file
    """
    if not hasattr(ensure_env_loaded, "_loaded"):
        load_env_file(env_filename)
        ensure_env_loaded._loaded = True


# Decorator to automatically load env for functions
def requires_env(*required_vars):
    """
    Decorator to ensure required environment variables are loaded

    Usage:
        @requires_env('DATABASE_URL', 'API_KEY')
        def my_function():
            # Function will have access to DATABASE_URL and API_KEY
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            ensure_env_loaded()

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables: {', '.join(missing_vars)}"
                )

            return func(*args, **kwargs)

        return wrapper
    return decorator
