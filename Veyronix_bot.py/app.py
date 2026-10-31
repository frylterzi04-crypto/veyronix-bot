import json
import os
import requests
from flask import Flask, render_template, request, jsonify
from duckduckgo_search import DDGS

app = Flask(__name__, static_folder='.', static_url_path='')

DATA_FILE = 'knowledge_base.json'

# --- BİLGİ TABANI İŞLEMLERİ ---
def load_knowledge():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "merhaba": "Merhaba! Ben VEYRONIX yapay zeka asistanı. Size nasıl yardımcı olabilirim?",
        "sen kimsin": "Ben VEYRONIX tarafından geliştirilmiş bir yapay zeka botuyum."
    }

def save_knowledge(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

knowledge_base = load_knowledge()

# --- DUCKDUCKGO İLE İNTERNET ARAMASI ---
def web_search_ai(query):
    try:
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, region='tr-tr', max_results=2))
            for item in search_results:
                title = item.get('title', '')
                href = item.get('href', '')
                body = item.get('body', '')
                results.append(f"<b><a href='{href}' target='_blank' style='color:#00d4ff;'>{title}</a></b><br>{body}")
        if results:
            return "<b>İnternet Araştırması Sonuçları:</b><br><br>" + "<br><br>".join(results)
    except Exception as e:
        print("Arama Hatası:", e)
        return "Arama sırasında bir hata oluştu."

# --- HAVA DURUMU SORGUSU ---
def get_weather():
    api_key = "cbdca0484b3fa0dd6f8f86665c4ca1d6"
    sehir = "Hatay"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={api_key}&units=metric&lang=tr"
    try:
        res = requests.get(url).json()
        derece = res["main"]["temp"]
        aciklama = res["weather"][0]["description"]
        return f"Şu an {sehir} için hava {aciklama} ve {derece}°C!"
    except:
        return "Hava durumu verisi alınamadı."

# --- ROTALAR ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip().lower()
    
    if not user_message:
        return jsonify({'response': 'Lütfen bir mesaj yazın.'})

    # 1. Eğitim Modu Kontrolü
    if user_message.startswith("öğret:"):
        try:
            content = user_message.replace("öğret:", "").strip()
            question, answer = content.split("|")
            knowledge_base[question.strip()] = answer.strip()
            save_knowledge(knowledge_base)
            return jsonify({'response': f'✅ Teşekkürler! "{question.strip()}" bilgisi hafızama eklendi.'})
        except ValueError:
            return jsonify({'response': '⚠️ Eğitim formatı hatalı. Kullanım: öğret: soru | cevap'})

    # 2. Yerel Hafıza Kontrolü
    response = knowledge_base.get(user_message)
    
    if not response:
        for q, a in knowledge_base.items():
            if q in user_message:
                response = a
                break

    # 3. Web Arama Kontrolü
    if not response:
        search_result = web_search_ai(user_message)
        if search_result:
            response = search_result
        else:
            response = "Üzgünüm, bu konuda internette açık bir bilgi bulamadım."

    return jsonify({'response': response})

# --- SOHBET TEMİZLEME ROTASI ---
@app.route('/clear',
           methods=['POST'])
def clear_chat():
    #şimdilik istemci tarafında ekran sıfırlanacağı için başarılı mesajı dönüyoruz
    return jsonify({'status': 'success', 'message': 'Sohbet temizlendi.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')