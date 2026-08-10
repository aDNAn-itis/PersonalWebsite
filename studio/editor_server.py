import os
import json
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer

class EditorHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            
            with open('animatic_config.json', 'r') as f:
                config = json.load(f)
                
            config["DEFAULT_COM_X"] = data.get("DEFAULT_COM_X", config["DEFAULT_COM_X"])
            config["DEFAULT_COM_Y"] = data.get("DEFAULT_COM_Y", config["DEFAULT_COM_Y"])
            
            new_configs = data.get("FRAME_CONFIGS", {})
            for k, v in new_configs.items():
                if k not in config["FRAME_CONFIGS"]:
                    config["FRAME_CONFIGS"][k] = {"dynamic": True}
                config["FRAME_CONFIGS"][k].update(v)
                
            with open('animatic_config.json', 'w') as f:
                json.dump(config, f, indent=4)
                
            print("Rebuilding frames...")
            subprocess.run(['python3', 'build_animatic.py'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

os.chdir('/home/adnan/Desktop/seji_web/interactive-portfolio/studio')
print("Starting Studio Editor Server on port 8000...")
HTTPServer(('', 8000), EditorHandler).serve_forever()
