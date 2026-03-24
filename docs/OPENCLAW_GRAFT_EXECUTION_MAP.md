# OPENCLAW_GRAFT_EXECUTION_MAP

Bu dosya, `upstream/openclaw` içine alınan kaynak koddan Graywolf'a kontrollü uyarlama için **uygulanabilir eşleme** dokümanıdır.

## Scope (Batch-1)
Hedef katmanlar:
1. Assistant/chat giriş davranışı
2. LLM karar sözleşmesi (structured output + fallback)
3. Kanal yanıt sözleşmesi (Telegram)
4. Tool orchestration üst-katman sinyali

## Upstream selected source anchors

### A) Assistant / message-flow anchors
- `upstream/openclaw/src/context-engine/*`
- `upstream/openclaw/src/infra/system-message.ts`
- `upstream/openclaw/src/infra/agent-events.ts`

Graywolf targets:
- `core/assistant_context.py`
- `core/graywolf_cli.py`
- `core/assistant_explainer.py`

Mode: adapted

### B) LLM integration / routing anchors
- `upstream/openclaw/src/cli/models-cli.ts`
- `upstream/openclaw/src/context-engine/*`
- `upstream/openclaw/src/infra/system-message.ts`

Graywolf targets:
- `core/llm_router.py`
- `core/graywolf_cli.py`
- `adapters/llm/*`

Mode: adapted

### C) Channel outbound anchors (Telegram UX)
- `upstream/openclaw/src/infra/outbound/message.ts`
- `upstream/openclaw/src/infra/outbound/format.ts`
- `upstream/openclaw/src/infra/outbound/sanitize-text.ts`
- `upstream/openclaw/src/infra/outbound/message-action-spec.ts`
- `upstream/openclaw/src/cli/send-runtime/telegram.ts`

Graywolf targets:
- `telegram_bot.py`
- `core/graywolf_cli.py` (assistant output contract)

Mode: adapted

### D) Tool orchestration anchors
- `upstream/openclaw/src/infra/outbound/tool-payload.ts`
- `upstream/openclaw/src/infra/outbound/message-action-runner.ts`
- `upstream/openclaw/src/infra/outbound/outbound-send-service.ts`

Graywolf targets:
- `core/graywolf_cli.py` (`orchestration_hint`)
- `core/orchestrator.py`
- `workflows/runner.py`

Mode: adapted (runtime spine untouched)

## Explicit non-goals (reference-only)
- `upstream/openclaw/src/gateway/*` (gateway runtime)
- `upstream/openclaw/src/extensions/*` plugin runtime wiring
- `upstream/openclaw/apps/*` mobile/desktop app stack

Bu katmanlar Graywolf'a bağımlılık olarak alınmayacak.

## Batch-1 concrete implementation order
1. Assistant output contract parity hardening (summary/next_step/triage/orchestration)
2. LLM decision schema strictness parity (json schema + intent normalization + fallback traces)
3. Telegram outbound formatting parity (sanitize + chunk + error/next-step visibility)
4. Tool payload visibility parity (non-breaking metadata only)

## Acceptance for Batch-1
- `tests/test_cli_agent_command.py` pass
- `tests/test_assistant_llm_decision.py` pass
- `tests/test_telegram_bot_bridge.py` pass
- `scripts/graywolf precheck` pass
