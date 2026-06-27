# Minecraft Self-Service Whitelist Portal

A self-service web portal for Minecraft players to add themselves to the server whitelist.

## Features
- **Frontend**: React + Vite + TailwindCSS, served by Nginx. Features a custom Minecraft aesthetic.
- **Backend**: Python Flask API connecting to the Minecraft server via RCON.
- **DDoS/Abuse Protection**: The backend enforces OWASP-recommended **Exponential Backoff Rate Limiting**. If an IP submits more than 5 requests in a minute, they are locked out for 60 seconds. Subsequent strikes double the lock duration (120s, 240s, etc.).
- **Customizable**: Set your server name via an environment variable, and write custom rules or instructions in a `.md` file that renders natively on the form!
- **Zero-Build Deployment**: Pre-built Docker images are automatically published to GitHub Container Registry (GHCR), meaning instant deployments without waiting for code to compile!

## Setup & Deployment

The easiest way to run this is using Docker Compose. This works perfectly on Linux, Windows, macOS, and NAS operating systems like **ZimaOS** or **CasaOS**.

1. **Get the Compose File**
   Download the `docker-compose.yml` file from this repository to your host machine. (You do not need to clone the entire repository).

2. **Configure Environment Variables**
   Open the `docker-compose.yml` file and modify the environment variables under the `backend` service to match your Minecraft server:
   ```yaml
      - RCON_HOST=your_minecraft_server_ip
      - RCON_PORT=25575
      - RCON_PASSWORD=your_rcon_password
      - PORTAL_NAME=My Custom Server
   ```
   *(Note: You can also pass these via an `.env` file or your ZimaOS/CasaOS Web UI).*

3. **Customize Instructions**
   Create an `instructions.md` file in the same folder as your `docker-compose.yml`. You can put your server rules, Discord links, or connection info here. It supports standard markdown and HTML `<details>` tags for collapsible sections. It will automatically be loaded by the server!

4. **Start the Services**
   Run the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   *If you are using ZimaOS/CasaOS, you can often just upload the `docker-compose.yml` file directly into the Web UI using the "Install a customized app" -> "Docker Compose" feature!*

   The frontend will be exposed on port `8080` locally (e.g., `http://localhost:8080`), which securely proxies `/api` requests to the backend.

5. **Expose to the Web**
   Use Nginx, Caddy, or Cloudflare Tunnels to route your domain (e.g., `whitelist.example.com`) to `localhost:8080` to allow players to access the form.