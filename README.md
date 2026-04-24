# 📅 Notion → Google Calendar Sync

> Notion'daki iş/staj başvurularını otomatik olarak Google Calendar'a senkronize eden, GitHub Actions üzerinde saatte bir çalışan hafif bir otomasyon sistemi.

---

## 🧠 Ne Yapar?

Notion'da tuttuğum **Staj - İş Başvuruları** veritabanındaki her kaydı okur; tarih bilgisi olan başvuruları Google Calendar'a etkinlik olarak ekler, günceller veya siler.

| Notion'da ne olursa | Calendar'da ne olur |
|---|---|
| Yeni başvuru + tarih eklendi | Etkinlik oluşturulur |
| Başvuru adı veya durumu değişti | Etkinlik güncellenir |
| Tarih silindi veya kayıt kaldırıldı | Etkinlik silinir |

---

## 🗂️ Notion Veritabanı

![Notion Screenshot](notion.png)

Kanban görünümündeki her kart bir başvuruyu temsil eder. Sistem şu alanları okur:

- **Name** — başvurulan pozisyon/şirket adı
- **Date** — başvuru veya mülakat tarihi
- **Status** — başvuru aşaması (Başvurulmadı, Başvuruldu, Eleme Aşamaları…)

---

## ⚙️ Nasıl Çalışır?

```
Notion API → sync.py → Google Calendar API
                ↑
     GitHub Actions (her saat)
```

1. `sync.py` Notion veritabanını sorgular
2. `sync_source=notion` etiketiyle işaretlenmiş mevcut Calendar etkinlikleriyle karşılaştırır
3. Farkları uygular: ekle / güncelle / sil
4. GitHub Actions bu scripti **saatte bir** otomatik çalıştırır

---

## 🔐 Kimlik Doğrulama

OAuth token'ları zamanla expire olduğu için sistem **Google Service Account** kullanır — kurulduktan sonra bir daha müdahale gerektirmez.

Gerekli GitHub Secrets:

| Secret | Açıklama |
|---|---|
| `NOTION_TOKEN` | Notion Integration token'ı |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account JSON anahtarı |

---

## 🚀 Kurulum

1. **Notion Integration** oluştur ve veritabanına erişim ver
2. **Google Cloud** üzerinde bir Service Account oluştur, JSON anahtarını indir
3. Google Calendar'ı service account e-postasıyla paylaş (`Make changes to events`)
4. GitHub Secrets'a `NOTION_TOKEN` ve `GOOGLE_SERVICE_ACCOUNT_JSON` ekle
5. Repo'yu fork'la veya kopyala — GitHub Actions otomatik devreye girer

---

## 🛠️ Teknolojiler

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-black?logo=githubactions)
![Notion API](https://img.shields.io/badge/Notion-API-black?logo=notion)
![Google Calendar](https://img.shields.io/badge/Google_Calendar-API-red?logo=googlecalendar)
