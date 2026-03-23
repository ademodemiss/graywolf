# OpenClaw Source Map (Phase 1 baseline)

Bu dosya, Graywolf'a graft/uyarlama sırasında OpenClaw kaynak izini takip etmek için kullanılır.

| Graywolf target | OpenClaw source | Mode | Status | Notes |
|---|---|---|---|---|
| core/graywolf_cli.py (assistant/chat karar katmanı) | openclaw message/agent flow davranış modeli | adapted | done | phase-2+6 acceptance tamamlandı |
| core/assistant_context.py | openclaw context assembly yaklaşımı | adapted | done | 100k clamp + summarized memory aktif |
| telegram_bot.py | openclaw channel UX yaklaşımı | adapted | done | phase-4+6 channel contract doğrulandı |
| core/llm_router.py | openclaw model routing/fallback yaklaşımı | adapted | done | phase-3+6 decision fallback doğrulandı |
| core/orchestrator.py + assistant orchestration_hint (graywolf_cli) | openclaw tool orchestration yaklaşımı | adapted | done | phase-5+6 orchestration hint doğrulandı |
| core/runtime.py | n/a | reference-only | locked | Graywolf çekirdeği korunacak |

## Rules
- Her fazda bu tablo güncellenecek.
- `Mode` yalnızca: `as-is`, `adapted`, `reference-only`.
- `Status` yalnızca: `planned`, `in-progress`, `done`.
