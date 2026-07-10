import os
import time
import logging
from functools import wraps
from flask import Flask, request, jsonify
from mcrcon import MCRcon

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
RCON_HOST = os.environ.get('RCON_HOST') or 'localhost'
rcon_port_env = os.environ.get('RCON_PORT')
RCON_PORT = int(rcon_port_env) if rcon_port_env and rcon_port_env.isdigit() else 25575
RCON_PASSWORD = os.environ.get('RCON_PASSWORD') or ''
PORTAL_NAME = os.environ.get('PORTAL_NAME') or 'MINECRAFT SERVER'
ENABLE_BEDROCK_PREFIX = os.environ.get('ENABLE_BEDROCK_PREFIX', 'false').lower() == 'true'
ENABLE_FLOODGATE = os.environ.get('ENABLE_FLOODGATE', 'false').lower() == 'true'

# --- RATE LIMITING ---
# IP -> { 'requests': [timestamps], 'strikes': int, 'locked_until': float }
RATE_LIMIT_DATA = {}
BASE_THRESHOLD = 5 # max requests per time window before a strike
TIME_WINDOW = 60 # time window in seconds
BASE_BACKOFF = 60 # base lock duration in seconds (will exponentially increase)

def exponential_backoff(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Determine client IP (using X-Forwarded-For if behind proxy, else remote_addr)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = '127.0.0.1'
            
        now = time.time()
        
        if ip not in RATE_LIMIT_DATA:
            RATE_LIMIT_DATA[ip] = {'requests': [], 'strikes': 0, 'locked_until': 0}
            
        user_data = RATE_LIMIT_DATA[ip]
        
        # 1. Check if currently locked
        if now < user_data['locked_until']:
            retry_after = int(user_data['locked_until'] - now)
            logger.warning(f"Rate limit enforced for IP {ip}. Locked for {retry_after} more seconds.")
            return jsonify({
                "error": "Too Many Requests", 
                "message": f"Rate limit exceeded. Please wait {retry_after} seconds before trying again."
            }), 429, {'Retry-After': str(retry_after)}
            
        # 2. Clean old requests outside the time window
        user_data['requests'] = [t for t in user_data['requests'] if now - t < TIME_WINDOW]
        
        # 3. Check threshold
        if len(user_data['requests']) >= BASE_THRESHOLD:
            # Threshold exceeded! Apply strike and exponential backoff
            user_data['strikes'] += 1
            # Exponential backoff: Base * (2 ^ (strikes - 1))
            lock_duration = BASE_BACKOFF * (2 ** (user_data['strikes'] - 1))
            user_data['locked_until'] = now + lock_duration
            
            # Clear requests so they start fresh after lock
            user_data['requests'] = []
            
            logger.warning(f"IP {ip} exceeded threshold. Strike {user_data['strikes']}. Locked for {lock_duration} seconds.")
            return jsonify({
                "error": "Too Many Requests", 
                "message": f"Rate limit exceeded. Please wait {lock_duration} seconds before trying again."
            }), 429, {'Retry-After': str(lock_duration)}
            
        # Add current request
        user_data['requests'].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---

@app.route('/api/config', methods=['GET'])
def get_config():
    instructions = ""
    try:
        if os.path.isfile('instructions.md'):
            with open('instructions.md', 'r') as f:
                instructions = f.read()
    except Exception as e:
        logger.error(f"Could not read instructions.md: {e}")
        
    return jsonify({
        "portal_name": PORTAL_NAME,
        "instructions": instructions
    })

@app.route('/api/whitelist', methods=['POST'])
@exponential_backoff
def whitelist_add():
    # 1. Input Validation
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'username' in request body."}), 400
        
    username = data['username'].strip()
    if username.startswith('.'):
        username = username[1:]
        
    if not username or len(username) > 16 or not username.replace('_', '').isalnum():
        return jsonify({"error": "Bad Request", "message": "Invalid Minecraft username."}), 400
        
    # 2. RCON Execution
    if not RCON_PASSWORD:
        logger.error("RCON_PASSWORD is not set in environment.")
        return jsonify({"error": "Server Error", "message": "Server configuration error."}), 500

    try:
        logger.info(f"Attempting to whitelist '{username}' and '.{username}'.")
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response1 = mcr.command(f"whitelist add {username}")
            logger.info(f"RCON Response for {username}: {response1}")
            
            if ENABLE_BEDROCK_PREFIX:
                response2 = mcr.command(f"whitelist add .{username}")
                logger.info(f"RCON Response for .{username}: {response2}")
            
            if ENABLE_FLOODGATE:
                response3 = mcr.command(f"fwhitelist add {username}")
                logger.info(f"RCON Response for fwhitelist: {response3}")
            
            return jsonify({
                "success": True, 
                "message": f"Successfully whitelisted {username}."
            }), 200
            
    except Exception as e:
        logger.error(f"RCON Connection failed: {e}")
        return jsonify({"error": "Server Error", "message": "Failed to connect to Minecraft server."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
