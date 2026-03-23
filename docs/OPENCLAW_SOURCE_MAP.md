# OpenClaw Source Map (Phase 1 baseline)

Bu dosya, Graywolf'a graft/uyarlama sırasında OpenClaw kaynak izini takip etmek için kullanılır.

| Graywolf target | OpenClaw source | Mode | Status | Notes |
|---|---|---|---|---|
| core/graywolf_cli.py (assistant/chat karar katmanı) | openclaw message/agent flow davranış modeli | adapted | in-progress | phase-2 chat contract iyileştirildi |
| core/assistant_context.py | openclaw context assembly yaklaşımı | adapted | in-progress | 100k clamp korunacak |
| telegram_bot.py | openclaw channel UX yaklaşımı | adapted | planned | Telegram parity hedefi |
| core/llm_router.py | openclaw model routing/fallback yaklaşımı | adapted | planned | provider bağımsız |
| core/runtime.py | n/a | reference-only | locked | Graywolf çekirdeği korunacak |

## Rules
- Her fazda bu tablo güncellenecek.
- `Mode` yalnızca: `as-is`, `adapted`, `reference-only`.
- `Status` yalnızca: `planned`, `in-progress`, `done`.
