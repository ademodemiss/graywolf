# Graywolf CLI Commands

## Core
- `graywolf status` → runtime/daemon/queue/approval durum özeti
- `graywolf doctor` → release precheck (zorunlu gate) çalıştırır
- `graywolf onboard` → ilk kurulum/smoke kontrolleri
- `graywolf approvals` → pending/granted/denied approval özeti
- `graywolf commands` → bu komut listesini terminalde gösterir

## Fast Operations
- `graywolf run --intent <intent> [--goal "..."] [--payload '{...}']` → hızlı komut tetikler
- `graywolf approve <request_id>` → pending onayı grant eder
- `graywolf deny <request_id>` → pending onayı deny eder
- `graywolf logs --target daemon|terminal|precheck [--lines 50]` → hızlı log okuma

## Quick Usage
```bash
/home/adem/graywolf/scripts/graywolf status
/home/adem/graywolf/scripts/graywolf doctor
/home/adem/graywolf/scripts/graywolf onboard
/home/adem/graywolf/scripts/graywolf approvals
/home/adem/graywolf/scripts/graywolf commands
/home/adem/graywolf/scripts/graywolf run --intent healthcheck --goal "günlük healthcheck"
/home/adem/graywolf/scripts/graywolf logs --target daemon --lines 20
```

## Note
Komut unutursan sadece şunu çalıştır:
```bash
/home/adem/graywolf/scripts/graywolf commands
```
