# Phase 266 Monitoring Checklist

Bu belge Phase 266’ya geçişte seni canlı tutacak, sadece okumak ve onaylamak için yazıldı. Adım adım ilerle ve her iş tamamlandığında kısa "tamam" yazman yeterli.

## 1. Öğrenme loglarını kontrol et
- `logs/self_improve_replan.log` (veya yeni `logs/self_improve_learning.log`) içeriğini haftalık periyotla gözden geçir. Her entry için `processed_by_phase265`, `learning_feedback`, `status` ve `duration_ms` alanlarının dolu olduğundan emin ol.
- Yeni işlerin (GRANTED entry'lerin) `processed_by_phase266` gibi bir bayrakla işaretlendiğini görürsen, Phase 266 otomasyon hattı aktif demektir.

## 2. Ops raporlarını doğrula
- Cron `monitor/replan_learning_reporter.py`/`monitor/replan_health_reporter.py` çalışıyorsa, Telegram/ops kanalındaki son raporu oku. Örneğin:
  - `learning_success_rate: %87`
  - `pending: 3`
  - `last_feedback: "approval.grant -> job completed"`
- Bu rakamlar makul (success rate yüksek, pending düşük) ise olay yok demektir; anormal bir sonuç çıkar (pending artıyor ya da success düşüyor) hemen haber ver.

## 3. Dashboard kartlarını kontrol et
- Dashboard’da `learning_success_rate`, `learning_pending`, `last_learning_feedback` kartlarının güncel veriler gösterdiğini doğrula.
- Eğer panelde veri yoksa (`N/A` yazıyorsa), backend script’lerinin log üretmediğini gösterir; hemen bildir.

## 4. Learning summary çıktısı
- `python monitor/replan_learning_summary.py --summary` (yeni script eklenirse) komutunu haftada bir çalıştırıp terminalde `Learning success rate: %X`, `Pending: Y`, `Last job: ...` gibi kısa özet al. Bu komut çalışmıyorsa ya da beklenmeyen çıktı veriyorsa beni uyar.

Bu üç kontrolü haftalık veya ihtiyaca göre tekrar et; ciddi bir sapma yoksa Phase 266 hattı stabil demektir. Hazırsan bir sonraki adımda Phase 267 planını da çıkarırım.