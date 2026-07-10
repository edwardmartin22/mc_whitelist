@app.route('/api/whitelist', methods=['POST'])
@exponential_backoff
def whitelist_add():
    # 1. Input Validation
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'username' in request body."}), 400
        
    username = data['username'].strip()
    
    # Strip the dot if they typed it manually
    if username.startswith('.'):
        username = username[1:]
        
    # FIX 1: Allow spaces in the alphanumeric check for Bedrock users
    if not username or len(username) > 16 or not username.replace('_', '').replace(' ', '').isalnum():
        return jsonify({"error": "Bad Request", "message": "Invalid Minecraft username."}), 400
        
    # 2. RCON Execution
    if not RCON_PASSWORD:
        logger.error("RCON_PASSWORD is not set in environment.")
        return jsonify({"error": "Server Error", "message": "Server configuration error."}), 500

    try:
        logger.info(f"Attempting to whitelist '{username}'")
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            
            # FIX 2: Wrap the username in quotes in case it has a space
            response = mcr.command(f'whitelist add "{username}"')
            logger.info(f"RCON Response for {username}: {response}")
            
            # FIX 3: Fallback logic! Catch the Java failure and try Floodgate
            if "Couldn't find profile" in response or "does not exist" in response:
                if ENABLE_FLOODGATE:
                    logger.info("Java profile not found. Attempting Floodgate fallback...")
                    fallback_response = mcr.command(f'fwhitelist add "{username}"')
                    logger.info(f"RCON Response for fwhitelist: {fallback_response}")
                    
                    # If Floodgate also fails
                    if "does not exist" in fallback_response or "Usage" in fallback_response:
                        return jsonify({"error": "Not Found", "message": f"Could not find Bedrock or Java player: {username}"}), 404
                else:
                    return jsonify({"error": "Not Found", "message": f"Could not find Java player: {username}"}), 404
            
            # If we used the Bedrock Prefix (legacy Geyser setup without Floodgate)
            elif ENABLE_BEDROCK_PREFIX and "Couldn't find profile" in response:
                 prefix_response = mcr.command(f'whitelist add ".{username}"')
                 logger.info(f"RCON Response for .{username}: {prefix_response}")
            
            return jsonify({
                "success": True, 
                "message": f"Successfully whitelisted {username}."
            }), 200
            
    except Exception as e:
        logger.error(f"RCON Connection failed: {e}")
        return jsonify({"error": "Server Error", "message": "Failed to connect to Minecraft server."}), 500
