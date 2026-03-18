# Archive Classification Matrix

Tarih: 2026-03-18
Amaç: archive ve docs/ops/archive içeriğini tek bakışta sınıflandırmak.

## Etiketler
- **COMPLETED**: Tarihsel olarak tamamlanmış, sadece referans.
- **PARTIAL**: Kısmen değerli, ama doğrudan aktif hatta bağlı değil.
- **PLAN**: Plan/not dokümanı, yürütülebilir kod değil.
- **JUNK**: Geçici/deneysel, operasyonel değeri düşük.

## archive/

| Yol | Sınıf | Not |
|---|---|---|
| `archive/runtime_legacy/*` | COMPLETED | Canonical runtime'a taşınmış eski hat |
| `archive/workflow_legacy/workflow_executor.py` | COMPLETED | Eski executor, aktifte `workflows/runner.py` |
| `archive/agent_legacy/*` | PARTIAL | Tarihsel prototip; aktifte yeniden yazılmış sürüm var |
| `archive/root_legacy/setup_tasks.py` | PLAN | Eski kurulum yaklaşımı |
| `archive/root_legacy/telegram_report.py` | PARTIAL | Eski raporlama akışı, referans olabilir |
| `archive/root_legacy/report_10m.py` | JUNK | Eski periodic script, canonical değil |
| `archive/root_legacy/update_openclaw_config.py` | JUNK | OpenClaw-spesifik, Graywolf core scope dışı |
| `archive/root_legacy/verify_phase*.py` | PLAN | Tarihsel faz doğrulama scriptleri |
| `archive/root_legacy/temp_gemini_test.py` | JUNK | Deneysel test |

## docs/ops/archive/

| Yol | Sınıf | Not |
|---|---|---|
| `docs/ops/archive/CURRENT_STATE.md` | COMPLETED | Arşivlenmiş durum dökümanı |
| `docs/ops/archive/NEXT_ACTION.md` | COMPLETED | Arşivlenmiş aksiyon listesi |
| `docs/ops/archive/ROADMAP.md` | COMPLETED | Arşivlenmiş roadmap |
| `docs/ops/archive/IMMEDIATE_VALIDATION.md` | PLAN | Tarihsel doğrulama planı |
| `docs/ops/archive/RELEASE_CHECKLIST.md` | PLAN | Tarihsel release checklist |
| `docs/ops/archive/no_break_intake/*` | JUNK | Temizlik turunda intake'e alınan loose not/artifact |

## Karar
- Active path dışı archive içeriği **korunur**, doğrudan silinmez.
- Yeni geliştirme sadece canonical path üzerinde yapılır.
- JUNK etiketli dosyalar için bir sonraki turda `archive/junk/` altına yeniden gruplama yapılabilir (opsiyonel).
