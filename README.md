Bu Python kodu, Flask web framework'ü kullanarak bir web uygulaması oluşturur. Uygulama, Türkçe metinlerde duygu analizi yapar ve sonuçları grafiklerle görselleştirir. İşte adım adım açıklaması:

Gerekli Kütüphaneler ve Ayarlar:

* Flask: Web uygulamasını oluşturmak için kullanılır.

* SentimentIntensityAnalyzer: NLTK'nin VADER duygu analiz aracıdır.

* GoogleTranslator: Metni Türkçeden İngilizceye çevirmek için kullanılır.

* matplotlib ve seaborn: Grafik oluşturmak için kullanılır.

* nltk: Doğal dil işleme için kullanılır.

* logging: Loglama yapmak için kullanılır.

Duygu Analizi ve Grafik Oluşturma Fonksiyonu:

Metni İngilizceye çevirir.

VADER ile duygu analizi yapar.

Analiz sonuçlarını grafikle görselleştirir ve static klasörüne kaydeder.

Formdan gelen metni alır ve analiz eder.

Analiz sonuçlarını ve grafiği döner.
![image](https://github.com/user-attachments/assets/24b6141d-90fe-4bbc-a89c-89d03886b9da)
Analiz etmek istediğimiz metnin analiz sonuçları gözükür
![image](https://github.com/user-attachments/assets/2d9df854-8702-4b7d-afec-f66450577d17)
Duygu skorları ile seaborn ve matplotlib ile duygu grafiği oluşturulur
![image](https://github.com/user-attachments/assets/1f69c76d-0d37-48fa-8eee-cfe413e0e536)


