import secrets
import string
import jwt
import time
import base64
import os
from typing import Dict

def generate_random_string(length: int = 40, include_special: bool = False) -> str:
    """Generate a random string of specified length."""
    alphabet = string.ascii_letters + string.digits
    if include_special:
        # Using only safe special characters that won't cause issues in .env files
        safe_special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        alphabet += safe_special
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length: int = 40) -> str:
    """Generate a random JWT secret of specified length."""
    return generate_random_string(length)

def generate_jwt(jwt_secret: str, role: str = "service_role", exp_hours: int = 168) -> str:
    """Generate a JWT token for Supabase."""
    current_time = int(time.time())
    payload = {
        "role": role,
        "iss": "supabase",
        "iat": current_time,
        "exp": current_time + (exp_hours * 3600)
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")

def generate_env_values() -> Dict[str, str]:
    """Generate all required environment variables."""
    # Generate JWT secret first as it's needed for other keys
    jwt_secret = generate_jwt_secret(40)
    
    # Generate all environment variables
    env_values = {
        # N8N Configuration
        "N8N_ENCRYPTION_KEY": generate_random_string(40),
        "N8N_USER_MANAGEMENT_JWT_SECRET": generate_random_string(40),
        
        # Supabase Secrets
        "POSTGRES_PASSWORD": generate_random_string(32, include_special=True),
        "JWT_SECRET": jwt_secret,
        "ANON_KEY": generate_jwt(jwt_secret, role="anon"),
        "SERVICE_ROLE_KEY": generate_jwt(jwt_secret, role="service_role"),
        "DASHBOARD_USERNAME": "admin",  # Can be changed by user if needed
        "DASHBOARD_PASSWORD": generate_random_string(16, include_special=True),
        
        # Supavisor
        "POOLER_TENANT_ID": generate_random_string(20),
        
        # Additional security keys
        "VAULT_ENC_KEY": generate_random_string(40),
        "SECRET_KEY_BASE": generate_random_string(64),
        "LOGFLARE_LOGGER_BACKEND_API_KEY": generate_random_string(40),
        "LOGFLARE_API_KEY": generate_random_string(40),
        
        # SMTP Configuration
        "SMTP_ADMIN_EMAIL": "admin@yourdomain.com",
        "SMTP_USER": generate_random_string(12),
        "SMTP_PASS": generate_random_string(16, include_special=True),
        "SMTP_SENDER_NAME": "Supabase Admin",
    }
    
    return env_values

def create_env_file(env_values: Dict[str, str]) -> None:
    """Create .env file from .env.example with generated values."""
    if not os.path.exists('.env.example'):
        raise FileNotFoundError(".env.example file not found!")
    
    with open('.env.example', 'r') as example_file:
        env_lines = example_file.readlines()
    
    # Process each line
    new_lines = []
    for line in env_lines:
        line = line.strip()
        if not line or line.startswith('#'):
            new_lines.append(line)
            continue
            
        # Check if line contains a key we need to replace
        for key, value in env_values.items():
            if line.startswith(f"{key}="):
                line = f"{key}={value}"
                break
        new_lines.append(line)
    
    # Write the new .env file
    with open('.env', 'w') as env_file:
        env_file.write('\n'.join(new_lines))

def main():
    try:
        print("Generating environment variables...")
        env_values = generate_env_values()
        
        print("Creating .env file...")
        create_env_file(env_values)
        
        print("\nSuccess! Your .env file has been created with the following values:")
        for key, value in env_values.items():
            print(f"\n{key}:")
            print(value)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 