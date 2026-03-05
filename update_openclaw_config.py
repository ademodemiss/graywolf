
import json
import os
import subprocess

config_path = os.path.expanduser('~/.openclaw/openclaw.json')

with open(config_path, 'r') as f:
    current_config = json.load(f)

current_config['agents']['defaults']['model']['primary'] = 'openai-codex/gpt-5.3-codex'
current_config['agents']['defaults']['model']['fallbacks'] = ['google/gemini-2.5-flash']

if 'auth' not in current_config:
    current_config['auth'] = {'profiles': {}}
if 'profiles' not in current_config['auth']:
    current_config['auth']['profiles'] = {}

current_config['auth']['profiles']['google:default']['provider'] = 'google'
current_config['auth']['profiles']['google:default']['mode'] = 'api_key'
current_config['auth']['profiles']['google:default']['apiKey'] = 'YOUR_GEMINI_API_KEY'

updated_config_json = json.dumps(current_config, indent=2)

with open(config_path, 'w') as f:
    f.write(updated_config_json)

try:
    subprocess.run(['openclaw', 'gateway', 'restart'], check=True)
    print("Gateway yeniden başlatma komutu gönderildi.")
except subprocess.CalledProcessError as e:
    print(f"Gateway yeniden başlatılamadı: {e.stderr}")
except FileNotFoundError:
    print("openclaw komutu bulunamadı. Lütfen PATH'inizde olduğundan emin olun.")

print("Config güncellendi.")
