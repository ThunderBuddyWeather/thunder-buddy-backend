"""
Script to automatically generate OpenAPI/Swagger specification from Flask routes
"""

import inspect
import logging
import os
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path BEFORE any other imports
root_dir = os.path.dirname(os.path.dirname(__file__))
logger.info(f"Root directory: {root_dir}")
sys.path.append(str(root_dir))
logger.info(f"Python path: {sys.path}")

try:
    from dotenv import load_dotenv  # noqa: E402
    
    # Load environment variables from .env.local if it exists
    env_path = os.path.join(root_dir, ".env.local")
    if os.path.exists(env_path):
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        logger.info("Loading environment from default .env")
        load_dotenv()  # fallback to .env
    
    # Set dummy DATABASE_URL for Swagger generation if not set
    if not os.environ.get("DATABASE_URL"):
        logger.info("Setting dummy DATABASE_URL for Swagger generation")
        os.environ["DATABASE_URL"] = "postgresql://dummy:dummy@localhost:5432/dummy"
    
    try:
        import yaml  # noqa: E402
    except ImportError:
        logger.info("PyYAML not installed. Installing now...")
        os.system("pip install PyYAML==6.0.1")
        import yaml  # noqa: E402
    
    # Import app after environment is loaded
    logger.info("Importing Flask app...")
    from main import app  # noqa: E402
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise


def analyze_route_params(func) -> list:
    """Analyze function source code to extract request parameters"""
    params = []
    try:
        source = inspect.getsource(func)
        
        # Parse request.args.get() calls
        for line in source.split("\n"):
            if "request.args.get" in line:
                try:
                    # Extract parameter details
                    param_str = line.split("request.args.get(")[1].split(")")[0]
                    param_parts = [p.strip().strip("\"'") for p in param_str.split(",")]
                    param_name = param_parts[0]
                    default_value = param_parts[1] if len(param_parts) > 1 else None
                    
                    # Check if parameter is required
                    is_required = "if not" in source and param_name in source
                    
                    params.append(
                        {
                            "in": "query",
                            "name": param_name,
                            "schema": {"type": "string", "default": default_value},
                            "required": is_required,
                            "description": f"Parameter {param_name}",
                        }
                    )
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to parse parameter from line: {line}. Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing route parameters: {str(e)}")
    
    return params


def analyze_responses(func) -> Dict[str, Any]:
    """Analyze function source code to determine possible responses"""
    responses = {}
    try:
        source = inspect.getsource(func)
        
        # Default 200 response
        responses["200"] = {
            "description": "Successful response",
            "content": {"application/json": {"schema": {"type": "object"}}},
        }
        
        # Look for error responses
        if 'return jsonify({"error"' in source or ", 400" in source:
            responses["400"] = {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                        }
                    }
                },
            }
        
        if ", 500" in source:
            responses["500"] = {
                "description": "Server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                        }
                    }
                },
            }
        
        # Look for other status codes
        for line in source.split("\n"):
            if "return" in line and "jsonify" in line:
                for code in ["201", "204", "401", "403", "404", "503"]:
                    if f", {code}" in line:
                        responses[code] = {
                            "description": get_status_description(code),
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
    except Exception as e:
        logger.error(f"Error analyzing responses: {str(e)}")
    
    return responses


def get_status_description(code: str) -> str:
    """Get standard description for HTTP status codes"""
    descriptions = {
        "200": "Successful response",
        "201": "Resource created",
        "204": "No content",
        "400": "Bad request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not found",
        "500": "Server error",
        "503": "Service unavailable",
    }
    return descriptions.get(code, "Unknown status code")


def analyze_route(func) -> Dict[str, Any]:
    """Analyze a route function to generate OpenAPI spec"""
    try:
        # Get function name and convert to title for summary
        func_name = func.__name__.replace("_", " ").title()
        
        # Get the first line of the function's docstring for description
        doc = inspect.getdoc(func)
        description = doc.split("\n", maxsplit=1)[0] if doc else func_name
        
        return {
            "summary": func_name,
            "description": description,
            "parameters": analyze_route_params(func),
            "responses": analyze_responses(func),
        }
    except Exception as e:
        logger.error(f"Error analyzing route {func.__name__}: {str(e)}")
        return {
            "summary": "Error analyzing route",
            "description": f"Error: {str(e)}",
            "parameters": [],
            "responses": {"500": {"description": "Server error"}}
        }


def generate_swagger():
    """Generate Swagger/OpenAPI specification from Flask routes"""
    try:
        # Ensure static directory exists
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        os.makedirs(static_dir, exist_ok=True)
        logger.info(f"Static directory ensured at: {static_dir}")
        
        spec = {
            "openapi": "3.0.2",
            "info": {
                "title": "Weather API",
                "version": "1.0.0",
                "description": "Weather API service providing current weather data",
                "contact": {"email": "your-email@example.com"},
            },
            "paths": {},
        }
        
        # Analyze all routes
        logger.info("Analyzing Flask routes...")
        with app.test_request_context():
            for rule in app.url_map.iter_rules():
                if rule.endpoint != "static":
                    try:
                        view_func = app.view_functions[rule.endpoint]
                        if not view_func:
                            continue
                        
                        path_spec = {}
                        for method in rule.methods - {"HEAD", "OPTIONS"}:
                            path_spec[method.lower()] = analyze_route(view_func)
                        
                        spec["paths"][str(rule)] = path_spec
                        logger.info(f"Analyzed route: {rule}")
                    
                    except (AttributeError, KeyError, TypeError) as error:
                        logger.error(f"Failed to analyze route {rule.endpoint}: {str(error)}")
                        continue
        
        # Write the spec to static/swagger.yaml
        swagger_path = os.path.join(static_dir, "swagger.yaml")
        logger.info(f"Writing swagger specification to: {swagger_path}")
        
        with open(swagger_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write("---\n")
            yaml.dump(
                spec,
                yaml_file,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                width=80,
            )
        
        # Verify the file was written
        if os.path.exists(swagger_path):
            file_size = os.path.getsize(swagger_path)
            logger.info(f"Successfully generated swagger.yaml ({file_size} bytes)")
            # Read and log the first few lines
            with open(swagger_path, 'r') as f:
                first_lines = ''.join(f.readlines()[:5])
                logger.info(f"First few lines of generated file:\n{first_lines}")
        else:
            raise FileNotFoundError(f"Failed to generate {swagger_path}")
        
    except Exception as e:
        logger.error(f"Error generating swagger specification: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Starting swagger.yaml generation...")
        generate_swagger()
        logger.info("Successfully completed swagger.yaml generation")
    except Exception as e:
        logger.error(f"Failed to generate swagger.yaml: {str(e)}")
        sys.exit(1)
