# Graywolf v2 Start Backlog (First 5 Jobs)

_Last updated: 2026-03-17_

Bağlam: Runtime cleanup tamamlandı (`76a124b`). Bu backlog canonical hat üstünde ilerlemek içindir.

## Job 1 — Runtime Kernel Entry (`core/runtime.py`)
**Amaç:** Tek giriş noktası ve lifecycle kontrolü.
- [x] `start/stop/status/run-once` arayüzü
- [x] `autonomous_loop + orchestrator + approval` bağlama katmanı (runtime `status` içinde approval health/pending görünürlüğü eklendi)
- [x] JSON durum çıktısı

**Done:** Worker/daemon komutları bu katmandan çağrılabiliyor.

## Job 2 — Unified Command Bus (CLI-first)
**Amaç:** Command -> Task -> Execution zincirini tek sözleşmede toplamak.
- [x] Komut şeması (`command_id`, `intent`, `payload`, `source`)
- [x] `task_queue` ile uyumlu dönüştürücü
- [x] Standart response şeması (`status`, `artifacts`, `errors`)

**Done:** `core.command_bus` + `core.runtime submit-command` ile CLI’den gelen komut canonical queue zincirine giriyor.

## Job 3 — Session State Layer
**Amaç:** Runtime içi stateful session yönetimi.
- [x] Basit session store (`sessions/*.json`)
- [x] Son komut, son sonuç, son hata, aktif görev alanları
- [x] Recovery/restart sonrası session restore

**Done:** `core.session_state` + `core.runtime --session-id` ile state dosyadan restore edilip güncelleniyor.

## Job 4 — Interface Adapters (Telegram/API) to Command Bus
**Amaç:** Tüm interface’leri aynı bus’a bağlamak.
- [x] Telegram adapter: command envelope üretimi
- [x] HTTP API adapter: aynı envelope/sözleşme
- [x] Adapter-level validation + audit log

**Done:** `adapters/interface/*` katmanı ve `dashboard/server.py` içindeki `/api/command` endpoint’i ile farklı girişler aynı command-bus sözleşmesine düşüyor.

## Job 5 — E2E Canonical Acceptance Suite
**Amaç:** v2’nin “tek sistem” davranışını kanıtlamak.
- [x] Senaryo 1: command al → task üret → execute → report
- [x] Senaryo 2: approval required → callback → continue
- [x] Senaryo 3: failure → replan/recovery → final report

**Done:** `scripts/e2e_canonical_acceptance.py` tek komutta koşuyor; rapor `reports/e2e_canonical_acceptance_latest.md` (PASS).

---

## Priority & Order
1. Job 1 (Runtime Kernel Entry)
2. Job 2 (Unified Command Bus)
3. Job 3 (Session State Layer)
4. Job 4 (Interface Adapters)
5. Job 5 (E2E Acceptance Suite)

## Rule
- OpenClaw sadece referans.
- Ürün sınırı ve runtime davranışı tamamen Graywolf içinde kalır.
