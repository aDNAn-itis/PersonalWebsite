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
            
            config_path = 'studio/animatic_config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            config["DEFAULT_COM_X"] = data.get("DEFAULT_COM_X", config["DEFAULT_COM_X"])
            config["DEFAULT_COM_Y"] = data.get("DEFAULT_COM_Y", config["DEFAULT_COM_Y"])
            
            new_configs = data.get("FRAME_CONFIGS", {})
            for k, v in new_configs.items():
                if k not in config["FRAME_CONFIGS"]:
                    config["FRAME_CONFIGS"][k] = {"dynamic": True}
                config["FRAME_CONFIGS"][k].update(v)
                
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            if "ASSETS" in data:
                with open('studio/scene_assets.json', 'w') as f:
                    json.dump(data["ASSETS"], f, indent=4)
                
            print("Rebuilding frames...")
            subprocess.run(['python3', 'build_animatic.py'], cwd='studio')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
        elif self.path == '/save_prompt':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            with open('studio/chatgpt_memory.txt', 'w') as f:
                f.write(data.get('prompt', ''))
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
        elif self.path == '/generate_asset':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                with open('studio/pending_request.json', 'w') as f:
                    json.dump(data, f)
                    
                print("\n" + "="*40)
                print(f"🤖 AI ASSET REQUEST RECEIVED!")
                print(f"Prompt: {data.get('prompt')}")
                print(f"Location: X={data.get('x')}, Y={data.get('y')}")
                print("="*40 + "\n")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'pending'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        elif self.path == '/check_status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists('studio/pending_request.json'):
                self.wfile.write(json.dumps({'status': 'pending'}).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({'status': 'done'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/get_prompt':
            try:
                with open('studio/chatgpt_memory.txt', 'r') as f:
                    prompt = f.read()
            except FileNotFoundError:
                prompt = ""
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'prompt': prompt}).encode('utf-8'))
        else:
            super().do_GET()

os.chdir('/home/adnan/Desktop/seji_web/interactive-portfolio')
print("Starting Studio Editor Server on port 8000...")
HTTPServer(('', 8000), EditorHandler).serve_forever()
