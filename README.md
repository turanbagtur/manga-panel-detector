# Manga Panel Otomatik Kesme Aracı (Panel Extraction)

Python ve OpenCV tabanlı manga panel otomatik tanıma ve kesme sistemi; Motion Comic projesi için geliştirilmiştir.

## Özellikler

- 🔍 **Akıllı Panel Tespiti**: Manga çerçevelerini hassas biçimde tanımak için uyarlamalı ikilileştirme ve morfolojik işlemler kullanır
- 📐 **Alan Filtreleme Algoritması**: Gürültü, konuşma balonları ve tam sayfa dış çerçeveleri otomatik olarak filtreler (%2-%80 alan aralığı)
- 📖 **Japon Manga Sıralaması**: Yukarıdan aşağıya, aynı satırda sağdan sola Japon manga okuma sırasını uygular
- 📁 **Çoklu Format Çıktısı**: Bağımsız panel resimleri, JSON veri dosyası ve görsel hata ayıklama görseli oluşturur
- ⚙️ **Ayarlanabilir Parametreler**: Komut satırından alan filtresi eşiklerini özelleştirmeyi destekler
- 🎨 **WebP Desteği**: WebP format giriş ve çıkışını tam olarak destekler
- 📦 **Toplu İşleme**: Tek resim, çoklu resim ve klasör bazlı işlemeyi destekler
- 🖱️ **Grafik Arayüz**: Tek tıkla başlatılan kullanıcı dostu GUI arayüzü

## Gereksinimler

- Python 3.7+
- Windows/Linux/macOS

## Hızlı Başlangıç

### 🚀 Tek Tıkla Başlat (Önerilen)

**Windows kullanıcıları:**
```powershell
# Çift tıklayarak çalıştırın veya komut satırında çalıştırın
start.bat
```

**Linux/macOS kullanıcıları:**
```bash
# Betiğe çalıştırma izni verin ve başlatın
chmod +x start_gui.sh
./start_gui.sh
```

### Manuel Kurulum

#### 1. Ortam Kurulumu

```powershell
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı etkinleştir (Windows)
.\venv\Scripts\activate

# Sanal ortamı etkinleştir (Linux/macOS)
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

#### 2. Uygulamayı Başlat

```powershell
# GUI arayüzünü başlat
python panel_detector_gui.py
```

## Kullanım

### Grafik Arayüz Sürümü (Önerilen)

Başlatıldıktan sonra üç girdi modundan birini seçebilirsiniz:

#### 🎯 Girdi Modları
- **Tek Resim**: Tek bir manga resim dosyası seçin
- **Çoklu Resim**: Birden fazla resim dosyasını toplu olarak seçin
- **Tüm Klasör**: Klasördeki tüm resimleri otomatik tarar

#### 🎨 Desteklenen Formatlar
- **Girdi Formatları**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`
- **Çıktı Formatları**: Giriş formatıyla eşleşir (WebP girişi WebP çıktısı, diğerleri JPG çıktısı)

#### 📋 İşlem Akışı
1. Girdi modunu seçin (Tek / Çoklu / Klasör)
2. "Gözat..." düğmesine tıklayarak resim veya klasör seçin
3. Tespit parametrelerini ayarlayın (isteğe bağlı)
4. "İşlemi Başlat" düğmesine tıklayın
5. İşlem sonuçlarını ve günlüğü inceleyin

### Komut Satırı Sürümü

```powershell
# Tek resim işle
python panel_detector.py --input manga_page.jpg

# Özel parametrelerle çalıştır
python panel_detector.py --input manga_page.jpg --min-area 0.01 --max-area 0.9
```

## Çıktı Dosyaları

### Tek Dosya İşleme
```
output/
├── panels/
│   ├── panel_01.jpg    # 1. panel (giriş formatıyla eşleşir)
│   ├── panel_02.jpg    # 2. panel
│   └── ...
├── panels_data.json    # Panel koordinat verileri
└── debug_result.jpg    # Hata ayıklama görsel çıktısı
```

### Toplu İşleme (Çoklu Resim / Klasör)
```
output/
├── panels/                       # Birleşik panel resimleri dizini
│   ├── dosyaadi1_panel_01.jpg    # 1. dosyanın 1. paneli
│   ├── dosyaadi1_panel_02.jpg    # 1. dosyanın 2. paneli
│   ├── dosyaadi2_panel_01.jpg    # 2. dosyanın 1. paneli
│   └── ...
├── dosyaadi1_debug.jpg           # 1. dosyanın hata ayıklama görseli
├── dosyaadi1_panels_data.json    # 1. dosyanın panel verileri
├── dosyaadi2_debug.jpg           # 2. dosyanın hata ayıklama görseli
├── dosyaadi2_panels_data.json    # 2. dosyanın panel verileri
└── ...
```

### panels_data.json Formatı
```json
[
  {
    "panel_id": 1,
    "x": 100,
    "y": 50,
    "width": 300,
    "height": 200
  }
]
```

## Bağımlılıklar

```
opencv-python  # Temel görüntü işleme kütüphanesi
numpy          # Sayısal hesaplama desteği
Pillow         # Görüntü işleme ve görüntüleme (WebP desteği dahil)
```

## Proje Yapısı

```
mangaAI/
├── panel_detector.py      # Temel tespit betiği (komut satırı sürümü)
├── panel_detector_gui.py  # GUI arayüz sürümü
├── start.bat              # Windows tek tıkla başlatma betiği
├── start_gui.sh           # Linux/macOS başlatma betiği
├── requirements.txt       # Bağımlılık listesi
├── README.md              # Proje açıklaması
└── venv/                  # Sanal ortam dizini (otomatik oluşturulur)
```

## Teknik Prensipler

### Görüntü Ön İşleme
1. **Gri Tonlamaya Çevirme**: Renkli görüntüyü gri tona dönüştürür
2. **Uyarlamalı İkilileştirme**: Gauss uyarlamalı eşikleme uygular
3. **Morfolojik İşlemler**: Kapama ve genişletme ile kopuk çerçeveleri birleştirir

### Kontur Tespiti ve Filtreleme
- Kapalı bölgeleri tespit etmek için `cv2.findContours` kullanır
- Alan filtresi: Tüm görüntünün %2-%80'ini kaplayan konturları korur
- Şekil filtresi: Aşırı ince veya düzensiz bölgeleri dışlar

### Japon Manga Sıralama Algoritması
1. Her panelin merkez noktası koordinatlarını hesapla
2. Y koordinatına göre gruplandırarak satırları belirle
3. Her satırda X koordinatına göre sağdan sola sırala
4. Tüm satırları Y koordinatına göre yukarıdan aşağıya sırala

## Sık Sorulan Sorular

### S: Hangi resim formatları destekleniyor?
C: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp` formatları desteklenmektedir.

### S: Bazı paneller tespit edilemiyor?
C: Minimum alan oranı parametresini düşürmeyi deneyin veya resim çözünürlüğünün çok düşük olmadığını kontrol edin.

### S: Çok fazla gürültü tespit ediliyor?
C: Minimum alan oranı parametresini artırın veya giriş resminin kalitesinin iyi olduğundan emin olun.

### S: Sıralama düzeni yanlış?
C: Algoritma Japon mangası için tasarlanmıştır; farklı bir sıralama gerekiyorsa sıralama algoritması değiştirilebilir.

### S: WebP formatı nasıl işleniyor?
C: Sistem WebP formatını otomatik olarak tanır; WebP girişi WebP formatında panel çıktısı üretir.

### S: Başlatma betiği çalışmıyor?
C: Python 3.7+ yüklü olduğundan emin olun ve bağımlılıkları yüklemek için ağ bağlantınızı kontrol edin.

## Lisans

Bu proje Motion Comic projesi için özel olarak geliştirilmiş olup yalnızca dahili kullanım içindir.

## Katkıda Bulunma

Algoritma performansını ve işlevselliğini geliştirmek için Issue ve Pull Request göndermekten çekinmeyin.