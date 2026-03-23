# OPENCLAW_GRAFT_PHASE0_2026-03-23

## 1) Faz
FAZ 0 — Graft/Fork stratejisi ve dosya eşleme

## 2) Faz hedefi
Graywolf ana repo/ürün korunarak, OpenClaw katmanlarının `aynen alınır / uyarlanır / referans` karar matrisiyle güvenli entegrasyon sırasını netleştirmek.

## 3) Yapılan analiz

### 3.1 Bugünkü Graywolf durumu (başlangıç)
- Çalışan çekirdek mevcut: CLI, assistant, agent loop, approval/resume, runtime queue/state, Telegram bridge.
- Son iyileştirmeler: hybrid triage, 100k context clamp, summarized memory assembly, Türkçe normalize triage fix.
- Sorun: ürün yönü dağılmaya açık; OpenClaw parity hedefi tek plana bağlanmalı.

### 3.2 Neden Graywolf başlangıç noktası
- Çalışan runtime spine zaten var (`core/runtime.py`, `core/command_bus.py`, `core/task_queue.py`, worker/daemon).
- Approval/continuity ve recovery tarafı üretimde kullanılabilir seviyede.
- Telegram girişi ve assistant entrypoint mevcut.
- Sıfırdan başlamak yüksek risk + yüksek süre kaybı.

### 3.3 OpenClaw katman sınıflandırması (hedef alınacak üst katman)
- Assistant/chat entry ve mesaj akışı
- LLM/provider entegrasyon desenleri
- chat-vs-task routing ve session-aware karar
- channel abstraction (özellikle Telegram deneyimi)
- tool orchestration (çağrı, çıktı, gözlemlenebilirlik)

### 3.4 Entegrasyon modeli (karar matrisi)

#### A) Aynen alınır (copy-as-is, lisans/attribution ile)
1. Lisans/attribution metinleri ve kaynak işaretleme şablonları
2. OpenClaw’dan doğrudan alınacak dokümantasyon referansları (mimari akış anlatımları)

#### B) Uyarlanır (graft/adapt)
1. Assistant/chat davranış kontratı (Graywolf `cmd_assistant` etrafında)
2. Chat-vs-task karar katmanı (session/context-aware)
3. LLM router/prompt contract yaklaşımı (Graywolf adapter yapısına uyar)
4. Channel UX kalıpları (Telegram çıktı/chunking/clarify)
5. Tool orchestration üst katmanı (runtime çekirdeğini bozmadan)

#### C) Sadece referans kalır
1. OpenClaw Gateway runtime/daemon altyapısı
2. OpenClaw’a özgü plugin/node transport ve provider-specific wiring
3. OpenClaw’ın doğrudan bağımlılık gerektiren control-plane parçaları

### 3.5 Graywolf korunacak çekirdek (dokunulmaz omurga)
- CLI/entry: `scripts/graywolf`, `core/graywolf_cli.py`
- Assistant ana akış: `core/graywolf_cli.py`, `core/assistant_context.py`
- Agent loop: `agent/simple_agent_loop.py`
- Approval/continuity: `core/approval.py`, `monitor/approval_callback_router.py`, `sessions/*`
- Runtime spine: `core/runtime.py`, `core/command_bus.py`, `core/task_queue.py`, `scripts/run_autonomy_worker.py`
- Policy: `policies/intent_policy.py`, `policies/shell_policy.py`
- Telegram bridge: `telegram_bot.py`
- Test/precheck: `tests/*`, `scripts/release_precheck.sh`

### 3.6 Graywolf ↔ OpenClaw katman eşleme (faz-0 mapping)
1. Assistant/chat
   - Graywolf: `core/graywolf_cli.py`, `core/assistant_context.py`, `core/assistant_explainer.py`
   - OpenClaw referans: message/session/agent loop davranış modeli (docs + dist katmanı)
   - Karar: **Uyarlanır**

2. LLM/provider
   - Graywolf: `core/llm_router.py`, `core/llm_factory.py`, `adapters/llm/*`
   - OpenClaw referans: model routing/fallback pattern
   - Karar: **Uyarlanır**

3. Routing (chat vs task)
   - Graywolf: `_triage_message_kind`, `_infer_goal_with_llm`, `agent/command_parser.py`
   - OpenClaw referans: inbound→session→queue→run karar disiplini
   - Karar: **Uyarlanır**

4. Channel
   - Graywolf: `telegram_bot.py`, assistant response contract
   - OpenClaw referans: outbound/send/runtime presentation pattern
   - Karar: **Uyarlanır**

5. Tool orchestration
   - Graywolf: `core/orchestrator.py`, `workflows/runner.py`, runtime submit path
   - OpenClaw referans: tool-call orchestration ve sonuç paketleme
   - Karar: **Kısmi uyarlama**

6. Gateway/node transport
   - Graywolf: mevcutte birebir karşılık yok
   - OpenClaw: gateway/websocket/node stack
   - Karar: **Sadece referans**

### 3.7 İlk güvenli entegrasyon sırası
1. Lisans/attribution çerçevesi netleştirme (FAZ 1)
2. Assistant/chat contract graft (FAZ 2)
3. LLM decision layer parity (FAZ 3)
4. Telegram channel UX parity (FAZ 4)
5. Tool orchestration üst katman uyarlaması (FAZ 5)
6. E2E acceptance + stabilizasyon (FAZ 6)
7. Canonical state freeze (FAZ 7)

## 4) Dokunulan dosyalar
- `reports/OPENCLAW_GRAFT_PHASE0_2026-03-23.md` (yeni)

## 5) Test/precheck
- Kod değişikliği olmadığı için test/precheck tetiklenmedi (analiz/dokümantasyon fazı).

## 6) Sonuç
- FAZ 0 tamamlandı.
- Graft/fork için tek entegrasyon modeli ve faz sırası netleşti.
- Graywolf çekirdeği korunarak OpenClaw üst katmanlarının nasıl alınacağı karara bağlandı.

## 7) Commit hash
- (Bu dosya commit edildikten sonra doldurulacak)

## 8) Kalan iş
- FAZ 1: lisans/attribution çerçevesini repo içinde resmi hale getirmek.

## 9) Sonraki faz
- FAZ 1 — Lisans/attribution + OpenClaw kaynak izi standardı
