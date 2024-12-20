from flask import Flask, render_template, request, send_from_directory
from nltk.sentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import seaborn as sns
import os
import nltk
import logging

# Gerekli NLTK sözlüğünü indir
nltk.download('vader_lexicon')

# Loglama ayarları
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

# Türkçe metni İngilizceye çeviren fonksiyon
def translate_turkish_to_english(text):
    try:
        return GoogleTranslator(source='tr', target='en').translate(text)
    except Exception as e:
        return f"Çeviri sırasında hata oluştu: {e}"

# Duygu analizi ve grafik oluşturma fonksiyonu
def sentiment_analyzer_and_plot(text):
    # Metni İngilizceye çevir
    translated_text = translate_turkish_to_english(text)
    logging.info(f"Translated Text: {translated_text}")

    # Eğer çeviri sırasında hata oluştuysa
    if "Çeviri sırasında hata oluştu" in translated_text:
        return translated_text, {'pos': 0, 'neu': 0, 'neg': 0}

    # VADER ile duygu analizi yap
    sentiment_scores = sia.polarity_scores(translated_text)
    logging.info(f"Sentiment Scores: {sentiment_scores}")

    # Duygu analiz sonuçlarını görselleştir
    labels = ['Pozitif', 'Nötr', 'Negatif']
    values = [sentiment_scores['pos'], sentiment_scores['neu'], sentiment_scores['neg']]

    # Seaborn ile grafik oluşturma
    plt.figure(figsize=(6, 4))
    sns.set_style("whitegrid")  # Stil ayarı
    sns.barplot(x=labels, y=values, palette=['green', 'gray', 'red'])
    plt.title('Duygu Analizi Sonuçları')
    plt.ylabel('Skor')
    plt.ylim(0, 1)

    # Statik dosya dizinini kontrol et
    if not os.path.exists('static'):
        os.makedirs('static')

    # Grafiği kaydet
    plt.savefig('static/sentiment_analysis.png')
    plt.close()  # Grafiği kapat

    # Compound skoruna göre duygu etiketi
    if sentiment_scores['compound'] >= 0.05:
        sentiment = "pozitif"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = "negatif"
    else:
        sentiment = "nötr"

    return sentiment, sentiment_scores

@app.route('/', methods=['GET', 'POST'])
def index():
    sentiment = ""
    scores = {'pos': 0, 'neu': 0, 'neg': 0}
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
                logging.error(f"Error during sentiment analysis: {e}")
                sentiment = "Duygu analizi sırasında bir hata oluştu."

    return render_template('index.html', sentiment=sentiment, scores=scores)

if __name__ == '__main__':
    app.run(debug=True)