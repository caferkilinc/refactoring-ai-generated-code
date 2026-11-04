# Project Genesis v3.0 — MIG-03 önkoşul raporu

| Alan | Değer |
|---|---|
| `REPORT_SCHEMA_VERSION` | 1 |
| `MIGRATION_ID` / `TASK_ID` | MIG-03 |
| `MIGRATION_TITLE` / `TASK_TITLE` | Automated Task Execution & Verification |
| `TASK_TYPE` | Codex-native geçiş |
| `SOURCE_MAIN_SHA` | `2f4eabd71b533519098dfee0817d933dbc23d148` |
| `WORKING_BRANCH` | `chore/1-genesis-v3-phase1` |
| `LOCAL_BASE_SHA` / `BASE_COMMIT` / `LOCAL_HEAD` | `cb2165f51edcc55176a124f3af8448bef0b0964e` |
| `AUTHORIZED_DEVELOPER` | Burkay Çakar, önceki geçiş çalışmasının geliştiricisi. Bu oturumda GitHub yazma kimliği yeniden doğrulanmadı. |
| `IMPLEMENTER` | Codex, önkoşul denetimi ve rapor |
| `STARTING_WORKTREE_STATE` | Temiz, tek worktree. Staged, unstaged, untracked veya ignored değişiklik ve devam eden Git işlemi gözlenmedi. |
| `IMPLEMENTATION_STATUS` | `BLOCKED` · zorunlu MIG-02 önkoşulları eksik |
| `LOCAL_VERIFICATION_STATUS` | MIG-03 için `NOT_RUN`. Mevcut 123 yönetişim testi `PASS`, mevcut pilot manifest kontrolü `FAIL`. |
| `HOSTED_VERIFICATION_STATUS` | `NOT_RUN` |
| `HUMAN_APPROVAL_STATUS` | `NOT_APPLICABLE` · incelenecek MIG-03 uygulaması yok |
| `PUBLICATION_STATUS` | Yayımlanmadı |
| `PHASE_LOCK_STATUS` | MIG-03 için kabul veya kilit kaydı yok |
| `FILES_CHANGED` | Yalnızca bu yeni rapor |

## Kaynak ve önkoşul kararı

Kanonik depo `caferkilinc/refactoring-ai-generated-code`. Ortam Windows 11 26H2, derleme 26300.9711, PowerShell 7.6.5 ve Git for Windows 2.56.0.windows.4. Yerel `main` canlı Git ve GitHub API sonucu ile eşleşti. Çalışma dalı için upstream yapılandırılmamış. Aynı adlı uzak dal, yukarıdaki yerel HEAD ile eşleşti. Etkin `core.autocrlf=input`. Donmuş girdi yollarının `-text` niteliği korundu.

| Önceki çalışma | Gözlenen durum |
|---|---|
| MIG-01 | `PUBLISHED` · yetki kapısı, yerel testler ve [v3 protokolü](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) geçiş dalında. Bu dal için PR gözlenmedi ve v3 değişiklikleri canlı `main`de yer almıyor. Kabul ve kilit kanıtı yok. |
| MIG-01B | `PUBLISHED` · [proje hafızası](../history/PROJECT_GENESIS_PROJECT_MEMORY_2026-11-04.md), [kilitleme eki](../governance/migrations/PHASE_1_HISTORY_AND_LOCKING_ADDENDUM.md) ve [faz tohumu](../governance/migrations/CODEX_NATIVE_PHASE_LEDGER_SEED.json) geçiş dalında. Tohum tarihsel veri. |
| MIG-02 | İncelenen Git kaynaklarında başlangıç uygulaması gözlenmedi. Faz tohumundaki durum `PLANNED`. |

`repo-bootstrap`, `task-context` ve `verification` için beklenen `.agents/skills/<ad>/SKILL.md` dosyaları çalışma ağacında, erişilebilir Git geçmişinde ve kanonik GitHub uzak deposunun ilan ettiği 11 dal ucunda bulunamadı. [development-handoff](../../.agents/skills/development-handoff/SKILL.md) mevcut. Sözleşmenin istediği üç becerinin çalışma biçimi ve entegrasyon arayüzü doğrulanamadığından `task-execution` oluşturulmadı. Yürürlükteki [v2.1 politika metni](../governance/PROJECT_GENESIS_ORCHESTRATOR_PROTOCOL_V2_1.md) ve mevcut GitHub kontrolleri üzerinden atlama yapılmadı. [Canlı ana dal](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/2f4eabd71b533519098dfee0817d933dbc23d148) · [Geçiş dalı](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/cb2165f51edcc55176a124f3af8448bef0b0964e)

## Geçmiş, faz durumu ve korunan kapsam

MIG-01’in [mevcut kapısı](../../scripts/governance/gate.py) PR yetkisi, yol kapsamı, CI ve salt okunur devir önerisi içeriyor. MIG-01B ekinde tanımlanan olay yazıcısı, yetkili faz kilidi ve yeniden açma mekanizması uygulanmış bir arayüz olarak gözlenmedi. Tarihsel tohumdan güncel kilit yetkisi veya kabul çıkarılmadı. Yeni olay ve katkı kaydı oluşturulmadı. İlgili SRS/mimari, yol haritası, durum, ADR ve devir kayıtları ürün bağlamı için incelendi.

Sabitlenmiş görev kaydında Alperen Enes Yaman, F02-CONTRACT / #11 için aktif geliştirici ve rotasyon indeksi 2. Kanonik kabul kayıtları #8 ve #9. MIG-03 bir ürün rotasyonu tüketmedi. Ürün kodu, önceki geçiş çalışmaları ve kök rapor korundu.

## Doğrulama ve kabul ölçütleri

| Kontrol | Sonuç ve kanıt |
|---|---|
| Kaynak ve yerel kapsam | `PASS` · `git status`, `git rev-parse`, `git remote -v`, `git worktree list`, `git config --show-origin`, `git ls-files --eol` ve `git ls-remote --refs`. |
| MIG-02 kaynak araması | `BLOCKED` · `git ls-remote`, `git cat-file`, `git ls-tree` ve `git log --all` ile üç beceri için uygulanmış kaynak bulunamadı. |
| Mevcut yönetişim ve depo hijyeni | `PASS` · `python -B -m unittest discover -s tests/governance` 123 test ve `python -B scripts/governance/security_check.py` başarılı. Bu sonuç mevcut geçiş dalına ait. |
| Korunan dosyalarda görev kaynaklı değişiklik | `PASS` · `git ls-tree` ve `git hash-object --no-filters` ile 24 korunan veya tarihsel dosya başlangıç commit’iyle bayt düzeyinde eşleşti. |
| Mevcut pilot bütünlüğü | `FAIL` · `python -B experiments/java-pilot/verify_integrity.py`, çıkış 1, `v0-source.json` manifest özeti uyuşmuyor. Kabul anındaki ağaçla karşılaştırmada dokuz önceden var olan fark görüldü. [Düzeltme PR’ı #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48) açık ve birleşmemiş. |
| MIG-03 yetki, yürütme, doğrulama, geçmiş, faz kilidi ve insan onayı testleri | `NOT_RUN` · Yeni yürütme bileşeni yok. Canlı Codex oturumu ve hosted MIG-03 doğrulaması yapılmadı. |

`AC-01`, `AC-04`, `AC-07`, `AC-12` (bu raporun Git farkı), `AC-16`, `AC-19`, `AC-22`, `AC-24` (önkoşul kanıtı) ve `AC-25` için mevcut denetim kanıtı yukarıda. `AC-11` için görev kaynaklı değişiklik yok, mevcut pilot bütünlük hatası sürüyor. Uygulama veya gerçek çalıştırma gerektiren diğer MIG-03 ölçütleri `BLOCKED` ya da `NOT_RUN`. Bir uygulama kabulü, yayın hazırlığı veya faz geçişi talep edilmiyor.

## Yeniden başlatma koşulu

Doğrulanabilir MIG-02 dalı veya commit’i ile üç becerinin gerçek kaynakları sağlandığında önkoşullar tekrar denetlenebilir. MIG-02 henüz uygulanmadıysa ayrı yetkiyle hazırlanması gerekir. İleride MIG-04’e devredilecek yayın girdisi, insan onayını görev, depo, dal, kaynak revizyonu ve gerçek dosya farkına bağlamalı. Bu rapor yayın yetkisi veya MIG-04 başlangıcı oluşturmaz.
