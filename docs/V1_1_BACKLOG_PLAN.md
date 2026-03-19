# Graywolf v1.1 Backlog Plan

Tarih: 2026-03-19
Prensip: v1.0 çekirdeğini bozmadan assistant UX katmanını güçlendirme.

## 1) Hedef Sınıflandırması

### A. Assistant UX Genişletme
- Sonuç açıklama dili (kısa/net/insan dili)
- Hata durumunda eylem önerili yanıt
- Komut unutma durumunda bağlamsal yardım

### B. Doğal Dil Görev Akışı İyileştirme
- Serbest metin -> intent güven skoru
- Belirsiz niyetlerde güvenli fallback/clarification
- Çok adımlı isteği küçük görevlere bölme (minimal)

### C. Terminal/Tool Deneyimini Akıllılaştırma
- En uygun komut önerisi (status/precheck/logs sırası)
- Tool başarısızlığında otomatik alternatif yol (ör. precheck raporundan aksiyon)
- Çıktıdan “kullanıcı özeti” otomatik üretme

### D. Sonuç Açıklama Kalitesi
- Standart yanıt şablonu (durum + ne yapıldı + sonraki adım)
- Policy/approval sonuçlarını kullanıcı dostu açıklama
- Teknik çıktıyı sade dile çevirme katmanı

## 2) Backlog Önceliklendirme

### Quick Wins (1-2 gün)
1. **Assistant response formatter** (merkezi özetleyici)
2. `graywolf run` çıktısı için kullanıcı dostu özet alanı
3. `graywolf approvals` çıktısında kısa karar önerisi
4. Dokümana “günlük kullanım cümleleri” bölümü ekleme

### Orta Vadeli (3-7 gün)
1. Basit intent confidence/fallback katmanı
2. Çok adımlı doğal dil isteği için hafif decomposer iyileştirmesi
3. Tool-failure -> remediation mapping tablosu
4. Assistant yanıt kalite testleri

### Ertelenecekler (v1.2+)
1. Geniş multi-agent orchestration
2. Büyük planlama motoru refactoru
3. Ağır RL/öğrenme katmanı
4. Yüksek maliyetli deneysel pipeline’lar

## 3) Uygulama Sırası (v1.1)
1. Wave-1: response quality foundation (formatter + test)
2. Wave-2: run/approval akışına formatter entegrasyonu
3. Wave-3: natural language fallback + confidence
4. Wave-4: tool remediation hints + kalite metrikleri

## 4) İlerleme Durumu (Canlı)
- [x] Wave-1: response quality foundation (formatter + test)
- [x] Wave-2: run/approvals UX summary entegrasyonu
- [x] Wave-3: parser confidence + safe fallback metadata
- [x] Wave-4 (kısmi): error remediation hints
- [x] Wave-4 devamı: approve/deny/status UX tutarlılığı
- [x] Dokümana “günlük kullanım cümleleri” bölümü
- [x] UX contract testleri (run/approvals/approve/deny/status/queue/monitor)
- [x] UX contract genişletmesi (doctor/report/help)
- [ ] Kalite metrikleri (yanıt netlik/checklist)

## 5) Günlük Kullanım Cümleleri (Quick Guide)
- "Sistemin genel durumunu hızlı göster" → `graywolf status`
- "Bekleyen işleri/kuyruğu özetle" → `graywolf queue --limit 10`
- "Onay bekleyen kritik işleri göster" → `graywolf approvals`
- "Bu isteği çalıştır" → `graywolf run --intent <intent> --goal "..."`
- "Daemon ayakta mı?" → `graywolf monitor status`
- "Hızlı sağlık kontrolü yap" → `graywolf precheck`

## 6) Güvenlik Sınırı
- Runtime core dosyalarında davranış değişikliği yapmadan ilerle
- Her wave sonunda `scripts/graywolf precheck` zorunlu
- Küçük commit, geri döndürülebilir değişiklik
