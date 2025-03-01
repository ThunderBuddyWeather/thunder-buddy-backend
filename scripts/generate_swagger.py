"""
Script to automatically generate OpenAPI/Swagger specification from Flask routes
"""

import glob
import inspect
import logging
import os
import sys
from typing import Any, Dict

from flask import Blueprint, Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
    
    # Create a temporary Flask app for route analysis
    logger.info("Creating temporary Flask app for route analysis...")
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dummy-secret-for-swagger')
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # Initialize extensions
    db = SQLAlchemy(app)
    ma = Marshmallow(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    limiter = Limiter(app=app, key_func=get_remote_address)
    CORS(app)
    
    # Add health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Check the health of the application by verifying database connectivity."""
        from scripts.db import test_connection as check_db_health
        
        db_health = check_db_health()
        is_healthy = (
            db_health["connection"] == "healthy"
            and db_health["query"] == "healthy"
        )
        
        health_status = {
            "status": "healthy" if is_healthy else "unhealthy",
            "components": {
                "api": {
                    "status": "healthy",
                    "message": "API service is running"
                },
                "database": db_health,
            },
        }
        
        http_status = 200 if health_status["status"] == "healthy" else 503
        return jsonify(health_status), http_status
    
    # Import all route files
    logger.info("Importing route files...")
    routes_dir = os.path.join(root_dir, "app", "Routes")
    route_files = glob.glob(os.path.join(routes_dir, "*_route.py"))
    route_files.extend(glob.glob(os.path.join(routes_dir, "*Route.py")))
    
    # Blueprint URL prefixes mapping
    blueprint_prefixes = {
        'user_account_blueprint': '/api/user',
        'friendship_blueprint': '/api/friends'
    }
    
    for route_file in route_files:
        module_name = os.path.splitext(os.path.basename(route_file))[0]
        logger.info(f"Importing route module: {module_name}")
        try:
            # Import the route module
            module = __import__(f"app.Routes.{module_name}", fromlist=["*"])
            
            # Find and register blueprints
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, Blueprint):
                    url_prefix = blueprint_prefixes.get(item_name, '')
                    logger.info(f"Registering blueprint {item_name} with prefix {url_prefix}")
                    app.register_blueprint(item, url_prefix=url_prefix)
        except Exception as e:
            logger.error(f"Error importing route module {module_name}: {str(e)}")
    
    logger.info("Flask app initialized successfully")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise


def generate_example_value(field_name, field_type="string"):
    """Generate example values for fields based on field name and type"""
    common_examples = {
        # User-related fields
        "username": "johndoe",
        "name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ssw0rd",
        "password_confirmation": "SecureP@ssw0rd",
        "user_id": 12345,
        
        # Friendship-related fields
        "friend_id": 54321,
        "friendship_status": "accepted",
        "status": "accepted",
        
        # Weather-related fields
        "location": "New York, NY",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "units": "metric",
        
        # Content-related fields
        "title": "Sample Title",
        "description": "This is a sample description for the item.",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "message": "Hello world!",
        
        # Common fields
        "id": 12345,
        "created_at": "2023-08-15T14:30:00Z",
        "updated_at": "2023-08-16T09:45:00Z",
    }
    
    # Check if we have a predefined example for this field
    if field_name in common_examples:
        return common_examples[field_name]
    
    # Generate based on field type and name patterns
    if field_type == "integer" or field_name.endswith("_id") or field_name == "id":
        return 12345
    elif field_type == "number":
        return 123.45
    elif field_type == "boolean" or field_name.startswith("is_") or field_name.startswith("has_"):
        return True
    elif field_name.endswith("_date") or "_date_" in field_name or field_name.endswith("_at"):
        return "2023-08-15T14:30:00Z"
    elif "email" in field_name:
        return "user@example.com"
    else:
        return "example value"

def infer_field_type(field_name, source_code):
    """Infer the field type based on field name and source code context"""
    # Default type is string
    field_type = "string"
    
    # Check for common patterns in field names
    if field_name.endswith("_id") or field_name == "id":
        field_type = "integer"
    elif field_name in ["latitude", "longitude", "price", "amount", "balance"]:
        field_type = "number"
    elif field_name.startswith("is_") or field_name.startswith("has_") or field_name in ["active", "enabled", "verified"]:
        field_type = "boolean"
    
    # Attempt to infer type from source code
    type_hints = {
        "int(": "integer",
        "float(": "number",
        "bool(": "boolean",
        "datetime.": "string",  # Dates are represented as strings in JSON
        "date": "string",       # Dates are represented as strings in JSON
    }
    
    for line in source_code.split("\n"):
        if field_name in line:
            for hint, hint_type in type_hints.items():
                if hint in line and field_name in line:
                    field_type = hint_type
                    break
    
    return field_type

def detect_get_json_fields(source, required_fields, optional_fields):
    """Detect fields from request.get_json() pattern"""
    for line in source.split("\n"):
        # Check for data = request.get_json() pattern
        if "request.get_json()" in line and "=" in line:
            var_name = line.split("=")[0].strip()
            # Look for field access in subsequent lines
            for next_line in source.split("\n"):
                if f"{var_name}[" in next_line or f"{var_name}.get(" in next_line:
                    try:
                        if f"{var_name}[" in next_line:
                            field = next_line.split(f"{var_name}[")[1].split("]")[0].strip("\"'")
                            # Skip 'field' as it's a variable name in the loop
                            if field != 'field' and field not in required_fields:
                                required_fields.append(field)
                        elif f"{var_name}.get(" in next_line:
                            field = next_line.split(f"{var_name}.get(")[1].split(")")[0].strip("\"'")
                            # Skip 'field' as it's a variable name in the loop
                            if field != 'field' and field not in optional_fields and field not in required_fields:
                                optional_fields.append(field)
                    except (IndexError, ValueError):
                        pass
        
        # Check for allowed_fields set definition
        if "allowed_fields" in line and "=" in line and "{" in line and "}" in line:
            try:
                fields_str = line.split("{")[1].split("}")[0]
                fields = [f.strip().strip("\"'") for f in fields_str.split(",")]
                for field in fields:
                    if field and field != 'field' and field not in optional_fields and field not in required_fields:
                        optional_fields.append(field)
            except (IndexError, ValueError):
                pass

def analyze_route_params(func) -> list:
    """Analyze function source code to extract request parameters"""
    params = []
    request_body = None
    try:
        source = inspect.getsource(func)
        
        # Check if route uses JWT authentication
        requires_auth = "@jwt_required" in source or "@jwt_required()" in source
        
        if requires_auth:
            # Add Authorization header parameter for JWT
            params.append({
                "in": "header",
                "name": "Authorization",
                "schema": {"type": "string"},
                "required": True,
                "description": "JWT Bearer token (format: Bearer <token>)"
            })
        
        # Parse request.args.get() calls for query parameters
        for line in source.split("\n"):
            if "request.args.get" in line:
                try:
                    # Extract parameter details
                    param_str = line.split("request.args.get(")[1].split(")")[0]
                    param_parts = [p.strip().strip("\"'") for p in param_str.split(",")]
                    param_name = param_parts[0]
                    default_value = param_parts[1] if len(param_parts) > 1 else None
                    
                    # Check if parameter is required
                    is_required = default_value is None or ("if not" in source and param_name in source)
                    
                    params.append({
                        "in": "query",
                        "name": param_name,
                        "schema": {"type": "string", "default": default_value},
                        "required": is_required,
                        "description": f"Parameter {param_name}"
                    })
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to parse parameter from line: {line}. Error: {str(e)}")
        
        # Check for request.json usage to identify body parameters
        if "request.json" in source or "request.get_json()" in source:
            # Look for data validation patterns to identify required fields
            required_fields = []
            optional_fields = []
            
            # Detect fields from request.get_json() pattern
            detect_get_json_fields(source, required_fields, optional_fields)
            
            # Pattern matching for required fields check
            for line in source.split("\n"):
                # Check for data = request.get_json() pattern
                if "request.get_json()" in line and "=" in line:
                    var_name = line.split("=")[0].strip()
                    # Look for field access in subsequent lines
                    for next_line in source.split("\n"):
                        if f"{var_name}[" in next_line or f"{var_name}.get(" in next_line:
                            try:
                                if f"{var_name}[" in next_line:
                                    field = next_line.split(f"{var_name}[")[1].split("]")[0].strip("\"'")
                                    if field not in required_fields:
                                        required_fields.append(field)
                                elif f"{var_name}.get(" in next_line:
                                    field = next_line.split(f"{var_name}.get(")[1].split(")")[0].strip("\"'")
                                    if field not in optional_fields and field not in required_fields:
                                        optional_fields.append(field)
                            except (IndexError, ValueError):
                                pass
                
                # Check for allowed_fields set definition
                if "allowed_fields" in line and "=" in line and "{" in line and "}" in line:
                    try:
                        fields_str = line.split("{")[1].split("}")[0]
                        fields = [f.strip().strip("\"'") for f in fields_str.split(",")]
                        for field in fields:
                            if field and field not in optional_fields and field not in required_fields:
                                optional_fields.append(field)
                    except (IndexError, ValueError):
                        pass
                
                if "if not" in line and "request.json" in line and "get(" in line:
                    # Extract field name from validation check
                    try:
                        field = line.split("request.json.get(")[1].split(")")[0].strip("\"'")
                        required_fields.append(field)
                    except (IndexError, ValueError):
                        pass
                elif "request.json.get(" in line or "request.json[" in line:
                    # Extract field name from usage
                    try:
                        if "request.json.get(" in line:
                            field = line.split("request.json.get(")[1].split(")")[0].strip("\"'")
                            if field not in required_fields:
                                optional_fields.append(field)
                        elif "request.json[" in line:
                            field = line.split("request.json[")[1].split("]")[0].strip("\"'")
                            if field not in required_fields:
                                required_fields.append(field)
                    except (IndexError, ValueError):
                        pass
            
            # Only create request body if we found fields
            if required_fields or optional_fields:
                # Filter out 'field' from required_fields
                required_fields = [f for f in required_fields if f != 'field']
                
                # Create JSON body schema
                properties = {}
                example_obj = {}
                
                for field in required_fields + optional_fields:
                    # Clean up field name by removing extra quotes and commas
                    clean_field = field.strip("'").strip('"').strip(',').strip(':').strip()
                    
                    # More aggressive cleaning for complex cases
                    if "'" in clean_field or '"' in clean_field or ',' in clean_field or ':' in clean_field:
                        # Extract the actual field name using regex if possible
                        import re
                        match = re.search(r'[\'"]?([a-zA-Z_][a-zA-Z0-9_]*)[\'"]?', clean_field)
                        if match:
                            clean_field = match.group(1)
                    
                    # Infer field type based on name and source code
                    field_type = infer_field_type(clean_field, source)
                    properties[clean_field] = {"type": field_type}
                    
                    # Generate example value
                    example_value = generate_example_value(clean_field, field_type)
                    example_obj[clean_field] = example_value
                
                # Create request body object (OpenAPI 3.0 format)
                request_body = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": required_fields,
                                "properties": properties
                            },
                            "example": example_obj
                        }
                    },
                    "description": "Request body parameters"
                }
                
    except Exception as e:
        logger.error(f"Error analyzing route parameters: {str(e)}")
    
    return params, request_body


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
        
        # Look for specific response structure patterns
        response_schemas = {}
        example_obj = {}
        
        for line in source.split("\n"):
            if "return" in line and "jsonify" in line:
                try:
                    # Try to extract response structure
                    if "{" in line and "}" in line:
                        response_str = line.split("jsonify(")[1].split(")", 1)[0]
                        if response_str.startswith("{") and ":" in response_str:
                            # Extract field names from response
                            fields = [f.strip().strip("\"'") for f in response_str.replace("{", "").replace("}", "").split(",") if ":" in f]
                            field_names = [f.split(":")[0].strip().strip("\"'") for f in fields]
                            
                            # Build basic schema from field names
                            properties = {}
                            for field in field_names:
                                if field:  # Skip empty field names
                                    field_type = infer_field_type(field, source)
                                    properties[field] = {"type": field_type}
                                    example_obj[field] = generate_example_value(field, field_type)
                            
                            if properties:
                                response_schemas = {
                                    "type": "object",
                                    "properties": properties
                                }
                except (IndexError, ValueError):
                    pass
                
                # Look for specific status codes
                for code in ["200", "201", "204", "400", "401", "403", "404", "409", "429", "500", "503"]:
                    if f", {code}" in line:
                        schema_content = {
                            "schema": response_schemas if response_schemas else {"type": "object"}
                        }
                        
                        # Add example if we have one
                        if example_obj:
                            schema_content["example"] = example_obj
                            
                        responses[code] = {
                            "description": get_status_description(code),
                            "content": {"application/json": schema_content},
                        }
        
        # Look for error responses if not already added
        if "400" not in responses and ('return jsonify({"error"' in source or ", 400" in source):
            error_example = {"error": "Bad request error message"}
            responses["400"] = {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                        },
                        "example": error_example
                    }
                },
            }
        
        if "401" not in responses and '@jwt_required' in source:
            auth_error_example = {"msg": "Missing Authorization Header"}
            responses["401"] = {
                "description": "Unauthorized - Missing or invalid authentication",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"msg": {"type": "string"}},
                        },
                        "example": auth_error_example
                    }
                },
            }
        
        if "500" not in responses and ", 500" in source:
            server_error_example = {"error": "Internal server error occurred"}
            responses["500"] = {
                "description": "Server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                        },
                        "example": server_error_example
                    }
                },
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
        "409": "Conflict",
        "429": "Too many requests",
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
        
        # Check if route requires authentication
        source = inspect.getsource(func)
        requires_auth = "@jwt_required" in source or "@jwt_required()" in source
        
        # Get parameters and request body
        parameters, request_body = analyze_route_params(func)
        
        route_spec = {
            "summary": func_name,
            "description": description,
            "parameters": parameters,
            "responses": analyze_responses(func),
        }
        
        # Add request body if present
        if request_body:
            route_spec["requestBody"] = request_body
        
        # Add security requirement for authenticated routes
        if requires_auth:
            route_spec["security"] = [{"bearerAuth": []}]
        
        return route_spec
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
                "title": "Thunder Buddy API",
                "version": "1.0.0",
                "description": "API service providing user accounts and friendship management",
                "contact": {"email": "your-email@example.com"},
            },
            "servers": [
                {
                    "url": "http://localhost:5000",
                    "description": "Local development server"
                },
                {
                    "url": "https://api.thunderbuddy.example.com",
                    "description": "Production API server"
                }
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT Bearer token authentication"
                    }
                },
                "schemas": {
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "message": {"type": "string"}
                        },
                        "example": {
                            "error": "Error message",
                            "message": "Additional error details"
                        }
                    },
                    "UserProfile": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "username": {"type": "string"}
                        },
                        "example": {
                            "user_id": 12345,
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "username": "johndoe"
                        }
                    },
                    "FriendshipStatus": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["pending", "accepted", "rejected"]},
                            "message": {"type": "string"}
                        },
                        "example": {
                            "status": "accepted",
                            "message": "Friend request accepted"
                        }
                    }
                }
            },
            "paths": {},
        }
        
        # Analyze all routes
        logger.info("Analyzing Flask routes...")
        
        # Create a mapping of route paths to their endpoint functions
        route_methods = {}
        
        with app.test_request_context():
            for rule in app.url_map.iter_rules():
                if rule.endpoint != "static":
                    # Initialize the path entry if it doesn't exist
                    path = str(rule)
                    if path not in route_methods:
                        route_methods[path] = {}
                    
                    # Add each HTTP method supported by this rule
                    for method in rule.methods - {"HEAD", "OPTIONS"}:
                        method_lower = method.lower()
                        if method_lower not in route_methods[path]:
                            try:
                                view_func = app.view_functions[rule.endpoint]
                                route_methods[path][method_lower] = view_func
                            except (AttributeError, KeyError):
                                logger.warning(f"Could not find view function for {rule.endpoint}")

            # Now analyze each route and method combination
            for path, methods in route_methods.items():
                path_spec = {}
                
                for method_lower, view_func in methods.items():
                    if view_func:
                        path_spec[method_lower] = analyze_route(view_func)
                
                # Format the path for OpenAPI (convert Flask's <int:id> to {id})
                openapi_path = path
                for arg in [a for r in app.url_map.iter_rules() if str(r) == path for a in r.arguments]:
                    # Get the rule that matches this path
                    matching_rule = next((r for r in app.url_map.iter_rules() if str(r) == path), None)
                    
                    if matching_rule and arg in matching_rule._converters:
                        arg_type = matching_rule._converters[arg].__class__.__name__.lower()
                        if arg_type == 'integerconverter':
                            arg_type = 'integer'
                        elif arg_type == 'stringconverter':
                            arg_type = 'string'
                        
                        # Replace Flask converter syntax with OpenAPI parameter syntax
                        openapi_path = openapi_path.replace(f'<{arg_type}:{arg}>', f'{{{arg}}}')
                        openapi_path = openapi_path.replace(f'<{arg}>', f'{{{arg}}}')
                        
                        # Add path parameter details if not already included
                        for method_spec in path_spec.values():
                            path_param_exists = any(p.get('name') == arg and p.get('in') == 'path' 
                                                 for p in method_spec.get('parameters', []))
                            
                            if not path_param_exists:
                                if 'parameters' not in method_spec:
                                    method_spec['parameters'] = []
                                    
                                method_spec['parameters'].append({
                                    'name': arg,
                                    'in': 'path',
                                    'required': True,
                                    'schema': {
                                        'type': arg_type if arg_type in ['integer', 'string'] else 'string'
                                    },
                                    'description': f'Path parameter: {arg}'
                                })
                
                spec["paths"][openapi_path] = path_spec
                logger.info(f"Analyzed route: {path}")
        
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
        
        # Also write as JSON for easy integration with Swagger UI
        swagger_json_path = os.path.join(static_dir, "swagger.json")
        logger.info(f"Writing swagger specification to: {swagger_json_path}")
        
        import json
        with open(swagger_json_path, "w", encoding="utf-8") as json_file:
            json.dump(spec, json_file, indent=2)
        
        # Verify the files were written
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
