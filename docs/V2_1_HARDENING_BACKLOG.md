# Graywolf v2.1 Hardening Backlog

## Goal
v2 foundation üstüne üretim güvenilirliğini artırmak.

## Top 5
1. Runtime reliability tests (approval edge cases + queue corruption guards)
2. Command policy hardening (intent-level policy + risk scoring)
3. Adapter resilience (retry/backoff + dead-letter queue)
4. CI expansion (runtime foundation tests + e2e acceptance as required checks)
5. Observability pack (runtime metrics snapshot + weekly trend report)

## Definition of done
- Release precheck + runtime tests CI’da yeşil
- Kritik operasyonlar için rollback/recovery playbook güncel
- v2.1 release note ve kanıt raporları hazır
