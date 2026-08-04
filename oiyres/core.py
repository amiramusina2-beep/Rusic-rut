import os
import json
import random
import urllib.request
import urllib.parse

class Rusic:
    def __init__(self, model_name="rut-0.3-normal"):
        self.model_name = model_name
        print(f"🎵 Инициализирована модель Oiyres Company: [{self.model_name}]")

    def _search_duckduckgo(self, query):
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'OiyresCompanyBot/1.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                abstract = data.get('AbstractText', '')
                related = [r.get('Text', '') for r in data.get('RelatedTopics', []) if 'Text' in r]
                return (abstract + " " + " ".join(related[:2])).strip()
        except:
            return ""

    def generate(self, prompt: str, use_web_search: bool = False, output_dir: str = "music"):
        """Единый метод генерации, подстраивающийся под выбранную версию модели"""
        os.makedirs(output_dir, exist_ok=True)
        prompt_lower = prompt.lower()
        
        # Сканируем локальный датасет папки music/
        all_notes = []
        all_tempos = []
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                if f.endswith('.json'):
                    try:
                        with open(os.path.join(output_dir, f), 'r', encoding='utf-8') as file:
                            song = json.load(file)
                            if 'notes' in song: all_notes.extend(song['notes'])
                            if 'tracks' in song:
                                for tr in song['tracks'].values(): all_notes.extend(tr)
                            if 'tempo' in song: all_tempos.append(song['tempo'])
                    except:
                        pass

        if not all_notes:
            all_notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

        # РЕЖИМ МОДЕЛИ: Rut 0.3 Normal (Классический, простой и быстрый)
        if self.model_name == "rut-0.3-normal":
            tempo = int(sum(all_tempos) / len(all_tempos)) if all_tempos else 110
            # Версия 0.3 выдает чистый моно-трек на одном базовом инструменте
            song_data = {
                "title": f"Rut 0.3 Normal: {prompt.capitalize()}",
                "model": "rut-0.3-normal",
                "tempo": tempo,
                "instrument": "acoustic_grand_piano",
                "notes": [random.choice(all_notes) for _ in range(8)]
            }
            filename = f"rut_03_{os.urandom(3).hex()}.json"

        # РЕЖИМ МОДЕЛИ: Rut 0.5 Pro (Продвинутый мультимикс + Web Search)
        elif self.model_name == "rut-0.5-pro":
            web_context = self._search_duckduckgo(prompt) if use_web_search else ""
            
            if any(word in prompt_lower for word in ['быстр', 'бодр', 'драйв', 'техно', 'бит']):
                tempo = random.randint(130, 160)
            else:
                tempo = int(sum(all_tempos) / len(all_tempos)) if all_tempos else 120

            available_instruments = ["acoustic_grand_piano", "violin", "electric_piano_1", "acoustic_guitar_steel", "synth_bass"]
            chosen_instruments = random.sample(available_instruments, k=random.randint(2, 3))
            
            tracks = {}
            for inst in chosen_instruments:
                tracks[inst] = [random.choice(all_notes) for _ in range(12)]

            prefix = "Rut 0.5 Pro [Web]" if (use_web_search and web_context) else "Rut 0.5 Pro [Local]"
            song_data = {
                "title": f"{prefix}: {prompt.capitalize()}",
                "model": "rut-0.5-pro",
                "tempo": tempo,
                "tracks": tracks
            }
            filename = f"rut_05_{os.urandom(3).hex()}.json"
        
        else:
            raise ValueError(f"Неизвестная модель: {self.model_name}. Доступные: 'rut-0.3-normal', 'rut-0.5-pro'")

        # Сохранение в локальный датасет
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(song_data, f, ensure_ascii=False, indent=2)
            
        print(f"🧠 [{self.model_name}] Трек сгенерирован и сохранен в '{filepath}'")
        return song_data