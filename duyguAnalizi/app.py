from flask import Flask, render_template, request
from nltk.sentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import seaborn as sns
import os
import nltk
import logging

# Gerekli NLTK sözlüğünü indiren kod parçası
nltk.download('vader_lexicon')

# Loglama ayarları yapılıyor
logging.basicConfig(level=logging.INFO)

# Flask uygulaması oluşturuluyor
app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

# "Korku" ile ilişkili kelimelerin listesini verdik korku için daha hassas bir analiz yapabilmek için
FEAR_KEYWORDS = ["korku", "korkutucu", "endişe", "panik", "dehşet", "kaygı"]

# Türkçe metni İngilizceye çeviren fonksiyon
def translate_turkish_to_english(text):
    try:
        return GoogleTranslator(source='tr', target='en').translate(text)
    except Exception as e:
        return f"Çeviri sırasında hata oluştu: {e}"

# Duygu analizi ve grafik oluşturma fonksiyonu oluşturuluyor
def sentiment_analyzer_and_plot(text):
    # Metni İngilizceye çevir
    translated_text = translate_turkish_to_english(text)
    logging.info(f"Translated Text: {translated_text}")

    # Eğer çeviri sırasında hata oluştuysa hata mesajını döndür
    if "Çeviri sırasında hata oluştu" in translated_text:
        return translated_text, {'pos': 0, 'neu': 0, 'neg': 0, 'fear': 0}

    # VADER ile duygu analizi yap ve sonuçları al
    sentiment_scores = sia.polarity_scores(translated_text)
    logging.info(f"Sentiment Scores: {sentiment_scores}")

    # "Korku" analizini metin üzerinde kontrol et ve sonucu kaydet
    fear_score = any(keyword in text.lower() for keyword in FEAR_KEYWORDS)
    sentiment_scores['fear'] = 1 if fear_score else 0

    # Duygu analiz sonuçlarını görselleştir ve kaydet
    labels = ['Pozitif', 'Nötr', 'Negatif', 'Korku']
    values = [
        sentiment_scores['pos'],
        sentiment_scores['neu'],
        sentiment_scores['neg'],
        sentiment_scores['fear']
    ]

    # Seaborn ile grafik oluşturma ve kaydetme
    plt.figure(figsize=(6, 4))
    sns.set_style("whitegrid")  # Stil ayarı
    sns.barplot(x=labels, y=values, palette=['green', 'gray', 'red', 'purple'])
    plt.title('Duygu Analizi Sonuçları')
    plt.ylabel('Skor')
    plt.ylim(0, 1)

    # Statik dosya dizinini kontrol et ve oluştur
    if not os.path.exists('static'):
        os.makedirs('static')

    # Grafiği kaydet ve dosya adını döndür
    plt.savefig('static/sentiment_analysis.png')
    plt.close()  # Grafiği kapat

    # Compound skoruna göre duygu etiketi belirle
    if sentiment_scores['fear'] == 1:
        sentiment = "korku"
    elif sentiment_scores['compound'] >= 0.05:
        sentiment = "pozitif"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = "negatif"
    else:
        sentiment = "nötr"

    return sentiment, sentiment_scores


# Ana sayfa için route oluşturuluyor ve metin alınıyor ve analiz ediliyor
@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    sentiment = ""
    scores = {'pos': 0, 'neu': 0, 'neg': 0, 'fear': 0}
    if request.method == 'POST':
        text = request.form['text']
        logging.info(f"Received text: {text}")

        if text.strip() == "":
            sentiment = "Lütfen bir metin girin."
        elif len(text) > 500:
            sentiment = "Lütfen 500 karakterden daha kısa bir metin girin."
        else:
            try:
                sentiment, sentiment_scores = sentiment_analyzer_and_plot(text)
                scores = sentiment_scores
            except Exception as e:
                logging.error(f"Duyarlılık analizi sırasında hata oluştu: {e}")
                sentiment = "Duygu analizi sırasında bir hata oluştu."

    return render_template('index.html', sentiment=sentiment, scores=scores)

# Uygulamayı çalıştır
if __name__ == '__main__':
    app.run(debug=True)
