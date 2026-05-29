#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manga Panel Otomatik Kesme Aracı - Grafik Arayüz Sürümü
Manga panel tespiti ve kesimi için kullanıcı dostu GUI arayüzü
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from PIL import Image, ImageTk
import cv2
import numpy as np
from panel_detector import PanelDetector


class PanelDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Manga Panel Otomatik Kesme Aracı")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Değişkenler
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="output")
        self.min_area = tk.DoubleVar(value=0.02)
        self.max_area = tk.DoubleVar(value=0.8)
        self.current_image = None
        self.preview_image = None
        self.processing = False
        self.input_files = []  # Birden fazla dosya yolunu sakla
        self.input_mode = tk.StringVar(value="single")  # single, multiple, folder
        
        self.setup_ui()
        
    def setup_ui(self):
        """Kullanıcı arayüzünü ayarla"""
        # Ana çerçeveyi oluştur
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst kontrol alanı
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Girdi seçim alanı
        input_frame = ttk.LabelFrame(top_frame, text="Girdi Seçimi", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seçim modu
        mode_frame = ttk.Frame(input_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(mode_frame, text="Seçim Modu:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Tek Resim", variable=self.input_mode, value="single").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Çoklu Resim", variable=self.input_mode, value="multiple").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Tüm Klasör", variable=self.input_mode, value="folder").pack(side=tk.LEFT, padx=5)
        
        # Dosya seçimi
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X)
        ttk.Label(file_frame, text="Girdi Yolu:").pack(side=tk.LEFT, padx=(0, 10))
        self.path_entry = ttk.Entry(file_frame, textvariable=self.input_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="Gözat...", command=self.browse_input).pack(side=tk.LEFT)
        
        # Dosya listesi (çoklu dosya modu)
        self.file_listbox = tk.Listbox(input_frame, height=4)
        self.file_listbox.pack(fill=tk.X, pady=(10, 0))
        self.file_listbox.pack_forget()  # Başlangıçta gizle
        
        # Çıktı dizini
        output_frame = ttk.Frame(input_frame)
        output_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(output_frame, text="Çıktı Dizini:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="Gözat...", command=self.browse_output).pack(side=tk.LEFT)
        
        # Parametre ayarları alanı
        params_frame = ttk.LabelFrame(top_frame, text="Tespit Parametreleri", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(fill=tk.X)
        
        # Birinci satır parametreler
        row1 = ttk.Frame(params_grid)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="Minimum Alan Oranı:").pack(side=tk.LEFT, padx=(0, 10))
        self.min_area_scale = ttk.Scale(row1, from_=0.001, to=0.1, variable=self.min_area, 
                                      orient=tk.HORIZONTAL, length=300)
        self.min_area_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.min_area_label = ttk.Label(row1, text=f"{self.min_area.get():.3f}", width=8)
        self.min_area_label.pack(side=tk.LEFT)
        
        # İkinci satır parametreler
        row2 = ttk.Frame(params_grid)
        row2.pack(fill=tk.X)
        
        ttk.Label(row2, text="Maksimum Alan Oranı:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_area_scale = ttk.Scale(row2, from_=0.1, to=1.0, variable=self.max_area,
                                      orient=tk.HORIZONTAL, length=300)
        self.max_area_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.max_area_label = ttk.Label(row2, text=f"{self.max_area.get():.3f}", width=8)
        self.max_area_label.pack(side=tk.LEFT)
        
        # Kaydırıcı olaylarını bağla
        self.min_area_scale.configure(command=lambda v: self.min_area_label.config(text=f"{float(v):.3f}"))
        self.max_area_scale.configure(command=lambda v: self.max_area_label.config(text=f"{float(v):.3f}"))
        
        # Düğme alanı
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="İşlemi Başlat", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Resmi Önizle", command=self.preview_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Çıktı Dizinini Aç", command=self.open_output_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Günlüğü Temizle", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Programı Kapat", command=self.close_app).pack(side=tk.RIGHT, padx=(10, 0))
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(top_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Ana içerik alanı (önizleme ve günlük)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Yatay bölünmüş PanedWindow oluştur
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol taraf: Resim önizleme
        preview_container = ttk.Frame(paned)
        paned.add(preview_container, weight=1)
        
        preview_label_frame = ttk.LabelFrame(preview_container, text="Resim Önizleme", padding="10")
        preview_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(preview_label_frame, text="Lütfen bir resim dosyası seçin", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Sağ taraf: İşlem günlüğü
        log_container = ttk.Frame(paned)
        paned.add(log_container, weight=1)
        
        log_label_frame = ttk.LabelFrame(log_container, text="İşlem Günlüğü", padding="10")
        log_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_label_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_input(self):
        """Girdi dosyasına/klasörüne gözat"""
        mode = self.input_mode.get()
        
        if mode == "single":
            # Tek resim seçimi
            filename = filedialog.askopenfilename(
                title="Manga Resmi Seç",
                filetypes=[
                    ("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("JPEG Dosyaları", "*.jpg *.jpeg"),
                    ("PNG Dosyaları", "*.png"),
                    ("WebP Dosyaları", "*.webp"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            if filename:
                self.input_path.set(filename)
                self.input_files = [filename]
                self.file_listbox.pack_forget()  # Dosya listesini gizle
                self.load_preview()
                
        elif mode == "multiple":
            # Çoklu resim seçimi
            filenames = filedialog.askopenfilenames(
                title="Birden Fazla Manga Resmi Seç",
                filetypes=[
                    ("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("JPEG Dosyaları", "*.jpg *.jpeg"),
                    ("PNG Dosyaları", "*.png"),
                    ("WebP Dosyaları", "*.webp"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            if filenames:
                self.input_files = list(filenames)
                self.input_path.set(f"{len(filenames)} dosya seçildi")
                self.file_listbox.pack(fill=tk.X, pady=(10, 0))  # Dosya listesini göster
                self.file_listbox.delete(0, tk.END)
                for filename in filenames:
                    self.file_listbox.insert(tk.END, os.path.basename(filename))
                # İlk resmi önizle
                if filenames:
                    self.load_preview(filenames[0])
                    
        elif mode == "folder":
            # Klasör seçimi
            dirname = filedialog.askdirectory(title="Manga Resimlerini İçeren Klasörü Seç")
            if dirname:
                # Klasördeki resim dosyalarını tara
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
                image_files = []
                
                for root, dirs, files in os.walk(dirname):
                    for file in files:
                        if os.path.splitext(file.lower())[1] in image_extensions:
                            image_files.append(os.path.join(root, file))
                
                if image_files:
                    self.input_files = image_files
                    self.input_path.set(f"{len(image_files)} dosya seçildi")
                    self.file_listbox.pack(fill=tk.X, pady=(10, 0))  # Dosya listesini göster
                    self.file_listbox.delete(0, tk.END)
                    for filename in image_files[:10]:  # Yalnızca ilk 10 dosya adını göster
                        self.file_listbox.insert(tk.END, os.path.basename(filename))
                    if len(image_files) > 10:
                        self.file_listbox.insert(tk.END, f"... ve {len(image_files) - 10} dosya daha")
                    # İlk resmi önizle
                    self.load_preview(image_files[0])
                else:
                    messagebox.showwarning("Uyarı", "Seçilen klasörde resim dosyası bulunamadı")
            
    def browse_output(self):
        """Çıktı dizinine gözat"""
        dirname = filedialog.askdirectory(title="Çıktı Dizinini Seç")
        if dirname:
            self.output_dir.set(dirname)
            
    def load_preview(self, image_path=None):
        """Resim önizlemesini yükle"""
        if not image_path:
            image_path = self.input_path.get()
            
        if not image_path or not os.path.exists(image_path):
            return
            
        try:
            # PIL ile resmi yükle ve boyutlandır
            image = Image.open(image_path)
            # En-boy oranını koruyarak ölçek hesapla
            max_size = 400
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Tkinter formatına dönüştür
            self.preview_image = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.preview_image)
            self.image_label.image = self.preview_image  # Referansı koru
            
            self.log(f"Resim yüklendi: {os.path.basename(image_path)}")
            
        except Exception as e:
            self.log(f"Resim yüklenemedi: {str(e)}")
            messagebox.showerror("Hata", f"Resim açılamadı: {str(e)}")
            
    def preview_image(self):
        """Seçili resmi önizle"""
        self.load_preview()
        
    def start_processing(self):
        """Resim işlemeyi başlat"""
        mode = self.input_mode.get()
        
        if mode == "single":
            if not self.input_path.get() or not os.path.exists(self.input_path.get()):
                messagebox.showerror("Hata", "Lütfen önce bir girdi resmi seçin")
                return
            self.input_files = [self.input_path.get()]
        else:
            if not self.input_files:
                messagebox.showwarning("Uyarı", "Lütfen önce girdi dosyaları veya klasör seçin")
                return
            
        if self.processing:
            messagebox.showwarning("Uyarı", "İşlem devam ediyor, lütfen bekleyin")
            return
            
        # Arayüzün donmaması için yeni iş parçacığında işle
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()
        
    def process_images(self):
        """Birden fazla resmi işleyen arka plan iş parçacığı"""
        self.processing = True
        self.process_button.configure(state='disabled')
        self.progress.start()
        
        try:
            total_files = len(self.input_files)
            self.log(f"{total_files} dosya işleniyor...")
            
            # Dedektörü oluştur
            detector = PanelDetector(
                min_area_ratio=self.min_area.get(),
                max_area_ratio=self.max_area.get()
            )
            
            total_panels = 0
            successful_files = 0
            panel_counter = 1  # Genel panel sayacı
            
            # Birleşik çıktı dizini oluştur
            unified_output_dir = self.output_dir.get()
            unified_panels_dir = os.path.join(unified_output_dir, "panels")
            os.makedirs(unified_panels_dir, exist_ok=True)
            
            for i, image_path in enumerate(self.input_files, 1):
                try:
                    self.log(f"[{i}/{total_files}] İşleniyor: {os.path.basename(image_path)}")
                    
                    # Tek dosyayı geçici dizinde işle
                    import tempfile
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Tespiti gerçekleştir
                        result = detector.detect_panels(image_path, temp_dir)
                        
                        # Panel resimlerini birleşik dizine taşı ve yeniden adlandır
                        if result['panel_paths']:
                            base_name = os.path.splitext(os.path.basename(image_path))[0]
                            
                            for j, panel_path in enumerate(result['panel_paths']):
                                # Yeni dosya adı oluştur: orijinal_dosya_adı_panel_sırası
                                new_filename = f"{base_name}_panel_{j+1:02d}.jpg"
                                new_panel_path = os.path.join(unified_panels_dir, new_filename)
                                
                                # Dosyayı birleşik dizine kopyala
                                import shutil
                                shutil.copy2(panel_path, new_panel_path)
                                
                                # Genel sayacı güncelle
                                panel_counter += 1
                            
                            total_panels += result['total_panels']
                            successful_files += 1
                            
                            self.log(f"  ✓ {result['total_panels']} panel tespit edildi")
                            
                            # İlk dosyaysa hata ayıklama önizlemesini yükle
                            if i == 1:
                                self.load_debug_preview(result['debug_path'])
                            
                            # Hata ayıklama sonucunu birleşik dizine kaydet
                            debug_filename = f"{base_name}_debug.jpg"
                            debug_dest = os.path.join(unified_output_dir, debug_filename)
                            if os.path.exists(result['debug_path']):
                                import shutil
                                shutil.copy2(result['debug_path'], debug_dest)
                            
                            # Panel verilerini birleşik dizine kaydet
                            data_filename = f"{base_name}_panels_data.json"
                            data_dest = os.path.join(unified_output_dir, data_filename)
                            if os.path.exists(result['panels_data_path']):
                                import shutil
                                shutil.copy2(result['panels_data_path'], data_dest)
                        
                except Exception as e:
                    self.log(f"  ✗ İşlem başarısız: {str(e)}")
                    continue
            
            # Özet sonuçları çıkar
            self.log(f"\nİşlem tamamlandı!")
            self.log(f"Başarıyla işlendi: {successful_files}/{total_files} dosya")
            self.log(f"Toplam tespit edilen panel: {total_panels}")
            self.log(f"Tüm panel resimleri şuraya kaydedildi: {unified_panels_dir}")
            self.log(f"Hata ayıklama ve veri dosyaları şuraya kaydedildi: {unified_output_dir}")
            
            # Çıktı dizinini açmak isteyip istemediğini sor
            if successful_files > 0 and messagebox.askyesno("Tamamlandı", f"İşlem tamamlandı!\n{successful_files} dosya başarıyla işlendi\nToplam {total_panels} panel\nÇıktı dizinini açmak ister misiniz?"):
                self.open_output_dir()
                
        except Exception as e:
            self.log(f"İşlem başarısız: {str(e)}")
            messagebox.showerror("Hata", f"İşlem sırasında hata oluştu:\n{str(e)}")
            
        finally:
            self.processing = False
            self.process_button.configure(state='normal')
            self.progress.stop()
            
    def load_debug_preview(self, debug_path):
        """Hata ayıklama sonucu önizlemesini yükle"""
        try:
            if os.path.exists(debug_path):
                image = Image.open(debug_path)
                # En-boy oranını koruyarak ölçek hesapla
                max_size = 400
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                self.preview_image = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self.preview_image)
                self.image_label.image = self.preview_image
                
                self.log("Hata ayıklama sonucu önizlemesi yüklendi")
        except Exception as e:
            self.log(f"Hata ayıklama önizlemesi yüklenemedi: {str(e)}")
            
    def open_output_dir(self):
        """Çıktı dizinini aç"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Windows
        else:
            messagebox.showwarning("Uyarı", "Çıktı dizini mevcut değil")
            
    def clear_log(self):
        """Günlüğü temizle"""
        self.log_text.delete(1.0, tk.END)
        
    def close_app(self):
        """Uygulamayı kapat"""
        if self.processing:
            if messagebox.askyesno("Onay", "İşlem devam ediyor, programı kapatmak istediğinizden emin misiniz?"):
                self.root.quit()
        else:
            self.root.quit()
        
    def log(self, message):
        """Günlük mesajı ekle"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()


def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = PanelDetectorGUI(root)
    
    # Pencere ikonunu ayarla (varsa)
    try:
        # root.iconbitmap("icon.ico")  # İkon dosyası eklenebilir
        pass
    except:
        pass
        
    # Pencereyi ortala
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
