# Minecraft Self-Service Whitelist Portal

A self-service web portal for Minecraft players to add themselves to the server whitelist.

## Features
- **Frontend**: React + Vite + TailwindCSS, served by Nginx. Features a custom Minecraft aesthetic.
- **Backend**: Python Flask API connecting to the Minecraft server via RCON.
- **Customizable**: Set your server name via an environment variable, and write custom rules or instructions in a `.md` file that renders natively on the form!

## Setup & Deployment

The easiest way to run this is using Docker Compose. This works perfectly on Linux, Windows, macOS, and NAS operating systems like **ZimaOS** or **CasaOS**.

1. **Clone the Repository**
   Pull the code directly from GitHub onto your host machine (or import it into your ZimaOS terminal):
   ```bash
   git clone https://github.com/edwardmartin22/mc_whitelist.git
   cd mc_whitelist
   ```

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
   Edit the `./backend/instructions.md` file. You can put your server rules, Discord links, or connection info here. It supports standard markdown and HTML `<details>` tags for collapsible sections. Since it's mounted as a Docker volume, you can edit this file on your host machine and it will update immediately!

4. **Start the Services**
   Run the application using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
   *If you are using ZimaOS/CasaOS, you can often just upload the `docker-compose.yml` file directly into the Web UI using the "Install a customized app" -> "Docker Compose" feature!*

   The frontend will be exposed on port `8080` locally (e.g., `http://localhost:8080`), which securely proxies `/api` requests to the backend.

4. **Expose to the Web**
   Use Nginx, Caddy, or Cloudflare Tunnels to route your domain (e.g., `whitelist.example.com`) to `localhost:8080` to allow players to access the form.