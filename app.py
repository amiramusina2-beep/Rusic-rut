import os
import json
import random
import urllib.request
import urllib.parse
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

MUSIC_DIR = os.path.join(os.path.dirname(__file__), 'music')
os.makedirs(MUSIC_DIR, exist_ok=True)

AVAILABLE_INSTRUMENTS = [
    "acoustic_grand_piano", 
    "violin", 
    "electric_piano_1", 
    "acoustic_guitar_steel",
    "flute",
    "synth_bass"
]

@app.route('/')
def index():
    files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.json')]
    return render_template('index.html', total_songs=len(files))

# Официальный и чистый поиск через легкий API DuckDuckGo (без лишних тяжелых библиотек)
def search_duckduckgo_json(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'OiyresCompanyBot/1.0'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            abstract = data.get('AbstractText', '')
            # Также соберем темы, если они есть
            related = [r.get('Text', '') for r in data.get('RelatedTopics', []) if 'Text' in r]
            combined = abstract + " " + " ".join(related[:2])
            return combined.strip()
    except Exception as e:
        print(f"Поиск DDG: интернет недоступен или выключен ({e})")
        return ""

@app.route('/generate_pure_autonomous', methods=['POST'])
def generate_pure_autonomous():
    data = request.json
    prompt = data.get('prompt', 'автономный трек')
    use_web_search = data.get('use_search', False)
    
    web_context = ""
    if use_web_search:
        print(f"🦆 Запрос к DuckDuckGo API для: {prompt}")
        web_context = search_duckduckgo_json(prompt)
        if web_context:
            print(f"✨ Получен контекст из сети: {web_context[:100]}...")

    files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.json')]
    
    # Собираем память нот из папки music/
    all_notes = []
    all_tempos = []
    
    for f in files:
        try:
            with open(os.path.join(MUSIC_DIR, f), 'r', encoding='utf-8') as file:
                song = json.load(file)
                if 'notes' in song: all_notes.extend(song['notes'])
                if 'tracks' in song:
                    for tr_notes in song['tracks'].values():
                        all_notes.extend(tr_notes)
                if 'tempo' in song: all_tempos.append(song['tempo'])
        except:
            pass

    if not all_notes:
        all_notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ['быстр', 'бодр', 'драйв', 'техно', 'бит', 'киберпанк']):
        tempo = random.randint(130, 160)
    elif any(word in prompt_lower for word in ['груст', 'медлен', 'эмбиент', 'спокок', 'расслаб']):
        tempo = random.randint(75, 95)
    else:
        tempo = int(sum(all_tempos) / len(all_tempos)) if all_tempos else 110

    # Мультиинструментальный микс
    chosen_instruments = random.sample(AVAILABLE_INSTRUMENTS, k=random.randint(2, 3))
    sample_size = random.choice([8, 12, 16])
    
    tracks = {}
    for inst in chosen_instruments:
        tracks[inst] = [random.choice(all_notes) for _ in range(sample_size)]

    title_prefix = "Rut 0.5 [Web+AI]" if (use_web_search and web_context) else "Rut 0.5 [Local AI]"
    autonomous_song = {
        "title": f"{title_prefix}: {prompt.capitalize()}",
        "tempo": tempo,
        "tracks": tracks
    }
    
    filename = f"rut_clean_{os.urandom(4).hex()}.json"
    filepath = os.path.join(MUSIC_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(autonomous_song, f, ensure_ascii=False, indent=2)

    total_files = len([f for f in os.listdir(MUSIC_DIR) if f.endswith('.json')])

    return jsonify({
        "status": "success", 
        "filename": filename, 
        "song": autonomous_song,
        "total_songs": total_files,
        "searched": use_web_search and bool(web_context)
    })

@app.route('/download_json/<filename>')
def download_json(filename):
    json_path = os.path.join(MUSIC_DIR, filename)
    if not os.path.exists(json_path):
        return "Файл не найден", 404
    return send_file(json_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)