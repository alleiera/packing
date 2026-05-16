# Packing List Generator

Gümrük işlemleri için koli listesi (Packing List) oluşturma ve saklama uygulaması.

## Kurulum Talimatları (Windows)

Uygulamanın çalışması için bilgisayarınızda Python yüklü olmalıdır.

1.  **Python Yükleyin:** [python.org](https://www.python.org/downloads/) adresinden Python 3.10 veya üzerini indirin ve kurun. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretlediğinizden emin olun.
2.  **Bağımlılıkları Yükleyin:** Terminal (PowerShell veya Komut İstemi) açın ve aşağıdaki komutu yapıştırıp Enter'a basın:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Uygulamayı Çalıştırın:** Uygulama klasöründeyken terminale şu komutu yazın:
    ```bash
    python main.py
    ```

## PDF ve Excel Çıktısı

- Uygulama, PDF çıktılarında Türkçe karakter uyumu için otomatik düzeltme yapar.
- Excel çıktıları tam uyumludur.
- Ayarlar kısmından şirket logonuzu ve bilgilerinizi güncellemeyi unutmayın.

## Hata Çözümü: ModuleNotFoundError: No module named 'fpdf'

Bu hata `fpdf2` kütüphanesinin yüklü olmadığını veya yanlış yüklendiğini gösterir. Yukarıdaki `pip install -r requirements.txt` komutunu çalıştırdığınızdan emin olun.
Eğer hala hata alıyorsanız doğrudan şu komutu deneyin:
```bash
pip install fpdf2
```
