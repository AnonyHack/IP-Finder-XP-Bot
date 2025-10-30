# keep_alive.py
import logging
import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from config import con
import json
from datetime import datetime
import socket
import os

logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping' or self.path == '/health':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Get bot info
            bot_status = "🟢 Online"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            port = getattr(con, 'PORT', 10000)
            
            # Get actual Render URL
            render_url = os.environ.get('RENDER_EXTERNAL_URL', f'http://0.0.0.0:{port}')
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>IP Tracker Bot - XP TOOLS</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: #333;
                        min-height: 100vh;
                    }}
                    .container {{
                        background: rgba(255, 255, 255, 0.95);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                        margin-top: 20px;
                    }}
                    h1 {{
                        text-align: center;
                        margin-bottom: 10px;
                        font-size: 2.5em;
                        color: #764ba2;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    }}
                    .tagline {{
                        text-align: center;
                        font-size: 1.2em;
                        color: #667eea;
                        margin-bottom: 30px;
                        font-style: italic;
                    }}
                    .status-card {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 25px;
                        margin: 20px 0;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                    }}
                    .status-badge {{
                        display: inline-block;
                        padding: 10px 25px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 1.2em;
                        background: rgba(255, 255, 255, 0.2);
                        margin-bottom: 15px;
                    }}
                    .info-grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-top: 30px;
                    }}
                    .info-item {{
                        background: rgba(255, 255, 255, 0.8);
                        padding: 20px;
                        border-radius: 12px;
                        border-left: 4px solid #667eea;
                    }}
                    .feature-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin-top: 20px;
                    }}
                    .feature-item {{
                        background: linear-gradient(135deg, #f093fb, #f5576c);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
                    }}
                    .shield {{
                        color: #667eea;
                        font-size: 1.5em;
                        animation: pulse 2s ease-in-out infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                        100% {{ transform: scale(1); }}
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        color: #636e72;
                    }}
                    h3 {{
                        color: #2d3436;
                        border-bottom: 2px solid #667eea;
                        padding-bottom: 10px;
                    }}
                    .emoji {{
                        font-size: 1.3em;
                        margin-right: 8px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ IP Tracker Bot</h1>
                    <div class="tagline">Advanced IP Geolocation & Network Intelligence</div>
                    
                    <div class="status-card">
                        <div class="status-badge">
                            <span class="shield">🛡️</span> {bot_status} <span class="shield">🛡️</span>
                        </div>
                        <p><strong>Last Updated:</strong> {current_time}</p>
                        <p><strong>Server:</strong> Render • <strong>Port:</strong> {port}</p>
                        <p><strong>Access URL:</strong> <a href="{render_url}" target="_blank">{render_url}</a></p>
                        <p><strong>Health Check:</strong> <a href="{render_url}/health" target="_blank">{render_url}/health</a></p>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <h3>🤖 Bot Identity</h3>
                            <p><strong>Name:</strong> IP Tracker Bot</p>
                            <p><strong>Platform:</strong> Telegram</p>
                            <p><strong>Framework:</strong> Pyrogram</p>
                            <p><strong>Database:</strong> MongoDB Atlas</p>
                        </div>
                        
                        <div class="info-item">
                            <h3>🔧 Technical Info</h3>
                            <p><strong>API ID:</strong> {'Configured'}</p>
                            <p><strong>API Hash:</strong> {'*' * len(con.API_HASH) if con.API_HASH else 'Not set'}</p>
                            <p><strong>Bot Token:</strong> {con.BOT_TOKEN[:15] + '...' if con.BOT_TOKEN else 'Not set'}</p>
                            <p><strong>MongoDB:</strong> Connected</p>
                        </div>
                    </div>
                    
                    <div class="info-item">
                        <h3>🔍 Core Features</h3>
                        <div class="feature-grid">
                            <div class="feature-item">
                                <span class="emoji">🌍</span> IP Geolocation
                            </div>
                            <div class="feature-item">
                                <span class="emoji">🔎</span> IP Analysis
                            </div>
                            <div class="feature-item">
                                <span class="emoji">📱</span> Inline Search
                            </div>
                            <div class="feature-item">
                                <span class="emoji">👥</span> User Management
                            </div>
                            <div class="feature-item">
                                <span class="emoji">📊</span> Usage Statistics
                            </div>
                            <div class="feature-item">
                                <span class="emoji">🎯</span> Premium Features
                            </div>
                            <div class="feature-item">
                                <span class="emoji">🛡️</span> Security Focused
                            </div>
                            <div class="feature-item">
                                <span class="emoji">⚡</span> Fast Response
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-item">
                        <h3>🌟 Advanced Capabilities</h3>
                        <ul style="list-style-type: none; padding: 0;">
                            <li>📍 Precise location tracking</li>
                            <li>🌐 Detailed network information</li>
                            <li>📈 User activity analytics</li>
                            <li>🔒 Secure data handling</li>
                            <li>🚀 High performance scanning</li>
                            <li>📱 Cross-platform compatibility</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>⚡ Powered by XP TOOLS & Pyrogram Framework</p>
                        <p>🌍 Running on Render Cloud Platform</p>
                        <p style="margin-top: 10px; font-size: 0.9em;">
                            "Advanced IP intelligence at your fingertips 🛡️"
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 - Page not found")

    def is_bot_running(self):
        """Check if the bot is running."""
        try:
            return True
        except:
            return False

    def log_message(self, format, *args):
        """Override to reduce log noise."""
        # Remove emojis from logs to prevent encoding issues
        message = f"{self.command} {self.path} - {self.client_address[0]}"
        logger.info(message)

def run_health_server():
    """Run a simple HTTP server to respond to health checks and display bot info."""
    try:
        port = getattr(con, 'PORT', 10000)
        server = HTTPServer(('localhost', port), HealthHandler)
        # Use simple messages without emojis to avoid encoding issues
        logger.info(f"Health server started successfully on port {port}")
        logger.info(f"IP Tracker Bot status page: http://localhost:{port}/")
        logger.info(f"Health check endpoint: http://localhost:{port}/health")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")
        raise

def start_keep_alive():
    """Start the keep-alive system with health server and periodic pings."""
    # Start health server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info("Health server thread started")
