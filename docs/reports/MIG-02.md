# Project Genesis v3.0 — MIG-02 Recovery

| Alan | Değer |
|---|---|
| `MIGRATION_ID` | MIG-02 |
| `SOURCE_MAIN_SHA` | `2f4eabd71b533519098dfee0817d933dbc23d148` |
| `LOCAL_BRANCH` | `chore/1-genesis-v3-phase1` |
| `LOCAL_HEAD` | `cb2165f51edcc55176a124f3af8448bef0b0964e` |
| `IMPLEMENTER` | Codex, kullanıcının MIG-02 kurtarma sözleşmesi kapsamında |
| `FILES_CREATED` | [repo-bootstrap](../../.agents/skills/repo-bootstrap/SKILL.md), [task-context](../../.agents/skills/task-context/SKILL.md), [verification](../../.agents/skills/verification/SKILL.md) ve bu rapor |
| `FILES_MODIFIED` | [development-handoff](../../.agents/skills/development-handoff/SKILL.md) |
| `VERIFICATION_RESULTS` | Yerel MIG-02 kontrolleri `PASS`. Gerçek Codex beceri keşfi ve macOS/Linux çalıştırması `NOT_RUN`. |
| `KNOWN_BLOCKERS` | Önceden var olan pilot manifest uyuşmazlığı. Bu girdiye bağlı kontroller `BLOCKED`. |
| `MIG-03_PREREQUISITES` | `READY` · üç beceri yerel dosya olarak mevcut, bağlantıları doğrulandı |
| `PUBLICATION_STATUS` | `NOT_PUBLISHED` |
| `PHASE_LOCK_STATUS` | `NOT_LOCKED` |

## Başlangıç ve kapsam

Windows 11 26H2 (26300.9711), PowerShell 7.6.5 ve Git for Windows 2.56.0.windows.4. Yerel HEAD ile GitHub’daki geçiş dalı eşleşti. Yerel `main`, uzak Git ref’i ve GitHub dal API’si aynı kaynak SHA’yı verdi. Tek worktree vardı. İlk durumda yalnızca izlenmeyen [MIG-03 önkoşul raporu](MIG-03.md) vardı. Staged, unstaged veya ilgili ignored değişiklik ve devam eden Git işlemi gözlenmedi. Raporun SHA-256 özeti başlangıçla eşleşti. Yerel `core.autocrlf=input` ve dondurulmuş dosyaların `-text` nitelikleri korundu. [Kaynak main](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/2f4eabd71b533519098dfee0817d933dbc23d148) · [Geçiş tabanı](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/cb2165f51edcc55176a124f3af8448bef0b0964e)

MIG-01 ve MIG-01B yayımlanmış geçiş dalında. Bunların kabul veya kilit durumu değiştirilmedi. [v3 protokolü](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) güvenilen `main` üzerinde etkinleşme koşulları sağlanana kadar öneri olarak ele alındı. [Proje hafızası](../history/PROJECT_GENESIS_PROJECT_MEMORY_2026-11-04.md) ve [faz tohumu](../governance/migrations/CODEX_NATIVE_PHASE_LEDGER_SEED.json) tarihsel kanıt. Aktif görev ve sahip, kanonik görev kaydından okundu. F02-CONTRACT / #11, Alperen Enes Yaman’a atanmış olarak kaldı. Rotasyon, kabul geçmişi ve ürün dosyaları korundu.

## Uygulama

- **repo-bootstrap** Git kaynağını ve çalışma ağacını ayrı doğrular, bilinen yerel değişiklikleri korur ve gerekirse takip referanslarına yazmadan gereken ref’i çeker.
- **task-context** zorunlu, teknik ve tarihsel bağlamı ayırır. Kritik kaynakların yolunu, revizyonunu, ilgisini ve doğrulama durumunu kaydeder.
- **verification** uygulanabilir gerçek komutları seçer, sonuçları ve çıkış kodlarını kaydeder, Git farkı ile korunan dosya baytlarını denetler.
- **development-handoff** bu becerileri tek görev akışında kullanır ve insan incelemesi sınırını korur. MIG-02 bir yürütme, yayın, kabul veya faz kilitleme otomasyonu eklemedi.

## Doğrulama kanıtı

| Komut veya senaryo | Sonuç |
|---|---|
| `git status`, `git rev-parse`, `git worktree list`, `git config --show-origin`, `git ls-remote --refs` | `PASS` · Kanonik kaynak, dal, başlangıç farkı ve çalışma ağacı doğrulandı. |
| `python -B -X utf8 -` ile geçici Git deposu ve salt okunur gerçek ref senaryoları | `PASS` · Eksik, yanlış ve kanonik uzak depo, temiz ve değişiklikli çalışma ağacı, korunmuş baytlar, 18/9 ayrışmış ref örneği. `git fetch --no-prune --no-tags --no-recurse-submodules --refmap= origin refs/heads/main` doğrulanan SHA’yı getirdi. Geçici deponun takip ref’leri ve çalışma ağacı değişmedi. |
| `python -B -X utf8 -` ile statik beceri ve salt okunur bağlam kontrolü | `PASS` · Dört farklı ad, basit YAML frontmatter yapısı, yerel bağlantılar, handoff referansları ve boşluklar kontrol edildi. F02 örneği sabitlenmiş görev kaydından #8’i seçti, ilgisiz adaptörleri dışarıda bıraktı. Eksik kaynak sorgusu sıfırdan farklı çıktı ve henüz mevcut olmayan `contract-checks.yml` başarılı sayılmadı. F02 yürütülmedi. |
| `python -B -m unittest discover -s tests/governance` | `PASS` · 123 mevcut yönetişim testi. |
| `python -B scripts/governance/check_docs.py`, `python -B scripts/governance/security_check.py`, `git diff --check` | `PASS` · Bağlantı, depo hijyeni ve izlenen farklar. Yeni dosyalar ayrıca statik boşluk kontrolünden geçti. |
| `git ls-tree`, `git hash-object --no-filters`, `Get-FileHash -Algorithm SHA256` | `PASS` · Korunan girdiler ve tarihsel kayıtlar başlangıçla bayt düzeyinde eşleşti. Geçici dosyada CRLF farkı algılandı. MIG-03 raporu korundu. |
| `python -B experiments/java-pilot/verify_integrity.py` | `FAIL` · Çıkış 1. Önceden var olan `v0-source.json` manifest özeti uyuşmazlığı yeniden üretildi. Bağımsız MIG-02 kontrolleri geçti. [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48) açık ve birleşmemiş. |
| Skill Creator `quick_validate.py` | Standart doğrulayıcı PyYAML eksikliği nedeniyle başlayamadı. Basit frontmatter için bağımlılıksız statik kontrol kullanıldı. |
| Canlı Codex keşfi, macOS/Linux çalıştırması ve GitHub Actions | `NOT_RUN` · Git komutları kabuktan bağımsız yazıldı ve Windows PowerShell’de denendi. |

MIG-02 yerel incelemeye hazır. MIG-03’ün eksik üç dosyası artık mevcut. Ayrı bir MIG-03 çalıştırması, kullanımdan önce kendi yetkisini, kaynak durumunu ve çalışma zamanı önkoşullarını yeniden doğrulamalı. Bu oturumda commit, push, PR, merge, görev kabulü, rotasyon ve faz kilitleme yapılmadı.
