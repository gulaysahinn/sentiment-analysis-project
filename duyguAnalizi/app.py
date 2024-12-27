from flask import Flask, render_template, request
from transformers import pipeline
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

# Flask uygulaması oluştur
app = Flask(__name__)

# Hugging Face ve NLTK duygu analizi modelleri
sentiment_pipeline = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
sia = SentimentIntensityAnalyzer()

# "Korku" ile ilişkili kelimelerin listesini verdik korku için daha hassas bir analiz yapabilmek için
FEAR_KEYWORDS = ["korku", "korkutucu", "endişe", "panik", "dehşet", "kaygı"]

# Türkçe metni İngilizceye çeviren fonksiyon
def translate_turkish_to_english(text):
    try:
        return GoogleTranslator(source='tr', target='en').translate(text)
    except Exception as e:
        logging.error(f"Çeviri sırasında hata oluştu: {e}")
        return None
# Ana sayfa rotası
# Duygu analizi ve grafik oluşturma fonksiyonu
def sentiment_analyzer_and_plot(text):
    # Metni İngilizceye çevir
    translated_text = translate_turkish_to_english(text)
    if not translated_text:
        return "Çeviri sırasında hata oluştu.", {}

    # Hugging Face duygu analizi yap
    analysis_results_hf = sentiment_pipeline(translated_text)
    logging.info(f"Hugging Face Analysis Results: {analysis_results_hf}")

    # NLTK duygu analizi yap
    sentiment_scores_nltk = sia.polarity_scores(translated_text)
    logging.info(f"NLTK Sentiment Scores: {sentiment_scores_nltk}")

    # Duyguları ve skorları ayrıştır ve birleştir
    scores_hf = {result['label']: result['score'] for result in analysis_results_hf}
    scores_nltk = {'pos': sentiment_scores_nltk['pos'], 'neu': sentiment_scores_nltk['neu'], 'neg': sentiment_scores_nltk['neg']}
    fear_score = any(keyword in text.lower() for keyword in FEAR_KEYWORDS)

    # Skorları normalize et
    total_score = sum(scores_hf.values()) + sum(scores_nltk.values()) + (1 if fear_score else 0)
    if total_score > 0:
        scores_hf = {label: score / total_score for label, score in scores_hf.items()}
        scores_nltk = {label: score / total_score for label, score in scores_nltk.items()}
        scores_hf['fear'] = (1 if fear_score else 0) / total_score

    # Duygular ve skorlar
    labels = ['Positive', 'Neutral', 'Negative', 'Fear']
    values = [
        scores_hf.get("joy", 0) + scores_hf.get("love", 0) + scores_nltk.get('pos', 0),  # Pozitif duygular
        scores_hf.get("neutral", 0) + scores_nltk.get('neu', 0),  # Nötr
        scores_hf.get("anger", 0) + scores_hf.get("sadness", 0) + scores_hf.get("disgust", 0) + scores_nltk.get('neg', 0),  # Negatif duygular
        scores_hf.get('fear', 0)  # Korku
    ]

    # Grafik oluşturma
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=values, palette=['green', 'gray', 'red', 'purple'])
    plt.title('Duygu Analizi Sonuçları')
    plt.ylabel('Skor')
    plt.ylim(0, 1)

    # Grafiği kaydet
    if not os.path.exists('static'):
        os.makedirs('static')
    plt.savefig('static/sentiment_analysis.png')
    plt.close()

    # En baskın duyguyu belirle
    dominant_emotion = max(scores_hf, key=scores_hf.get)
    if dominant_emotion in ["anger", "sadness", "disgust"]:
        dominant_emotion = "Negative"
    elif dominant_emotion in ["joy", "love"]:
        dominant_emotion = "Positive"
    elif dominant_emotion == "neutral":
        dominant_emotion = "Neutral"
    else:
        dominant_emotion = "Fear"

    return dominant_emotion, {**scores_hf, **scores_nltk}


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    sentiment = ""
    scores = {}
    if request.method == 'POST':
        text = request.form['text']
        if not text.strip():
            sentiment = "Lütfen bir metin girin."
        elif len(text) > 500:
            sentiment = "Lütfen 500 karakterden daha kısa bir metin girin."
        else:
            try:
                sentiment, scores = sentiment_analyzer_and_plot(text)
            except Exception as e:
                logging.error(f"Hata: {e}")
                sentiment = "Duygu analizi sırasında bir hata oluştu."

    return render_template('index.html', sentiment=sentiment, scores=scores)

# Uygulamayı çalıştır
if __name__ == '__main__':
    app.run(debug=True)
