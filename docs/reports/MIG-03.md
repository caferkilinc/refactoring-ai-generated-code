# Project Genesis v3.0 — MIG-03 Resume

| Alan | Değer |
|---|---|
| `MIGRATION_ID` | MIG-03 |
| `ATTEMPT` | 2 |
| `PREVIOUS_STATUS` | `BLOCKED` · MIG-02 becerileri eksikti |
| `CURRENT_STATUS` | `LOCALLY_VERIFIED` · insan incelemesi bekliyor |
| `SOURCE_MAIN_SHA` | `2f4eabd71b533519098dfee0817d933dbc23d148` |
| `WORKING_BRANCH` | `chore/1-genesis-v3-phase1` |
| `LOCAL_HEAD` | `cb2165f51edcc55176a124f3af8448bef0b0964e` |
| `MIG02_PREREQUISITES` | `MIG03_PREREQUISITES_READY` |
| `IMPLEMENTATION_STATUS` | Tek görev yürütme becerisi, yerel denetim yardımcısı ve testler hazır |
| `FILES_CREATED` | [task-execution](../../.agents/skills/task-execution/SKILL.md), [task_execution.py](../../scripts/governance/task_execution.py), [test_task_execution.py](../../tests/governance/test_task_execution.py), [ilk deneme arşivi](MIG-03-ATTEMPT-1-BLOCKED.md) |
| `FILES_MODIFIED` | [development-handoff](../../.agents/skills/development-handoff/SKILL.md) ve bu rapor |
| `AUTHORIZATION_TESTS` | `PASS` · doğru görev ve geliştirici, yanlış depo/kimlik/görev/taban, eksik önkoşul ve korumalı kapsam |
| `EXECUTION_TESTS` | `PASS` · incelemeye geçiş, eksik bağlam, kapsam dışı fark, mevcut kullanıcı dosyasının korunması |
| `VERIFICATION_TESTS` | `PASS` · gerçek çıkış kodu 7, çalışmayan zorunlu kontrol, beklenmedik dosya yazımı ve korunan bayt farkı |
| `HISTORY_TESTS` | `PASS` · ürün/geçiş ayrımı, yerel MIG-02 önkoşulu, olay/kabul/rotasyon yazılmaması |
| `APPROVAL_TESTS` | `PASS` · insan kararı beklenmesi, yanlış kişi/inceleme kimliği, ret kaydı ve değişen içerikle eski onayın reddi |
| `LOCAL_VERIFICATION` | `PASS` · 136 yönetişim testi, gerçek depoda salt okunur MIG-03 başlangıç kontrolü, metadata, bağlantılar, hijyen ve fark denetimi |
| `HOSTED_VERIFICATION` | `NOT_RUN` |
| `PILOT_INTEGRITY_STATUS` | `FAIL` · önceden var olan `v0-source.json` manifest uyuşmazlığı |
| `PROTECTED_FILE_STATUS` | `PASS` · başlangıçtaki korunan baytlar, geçmiş ve kayıtlar korundu |
| `HUMAN_APPROVAL_STATUS` | `HUMAN_APPROVAL_PENDING` |
| `PUBLICATION_STATUS` | `NOT_PUBLISHED` |
| `PHASE_LOCK_STATUS` | `NOT_LOCKED` |
| `MIG04_READINESS` | `BLOCKED` · inceleme ve ayrı yürütme/yayın yetkisi bekliyor. Yerel kanıt arayüzü belgelendi. |

## Başlangıç ve geçmiş

Windows 11, PowerShell 7.6.5, Git for Windows 2.56.0.windows.4 ve Python 3.14.5 kullanıldı. Tek worktree vardı. Önceden var olan MIG-02 becerileri, MIG-02 raporu, handoff entegrasyonu ve ilk MIG-03 raporu başlangıç kapsamına alındı. Staged fark, ilgili ignored çıktı veya devam eden Git işlemi gözlenmedi. Git ve GitHub API, kaynak `main` SHA’sında uzlaştı. Uzak geçiş dalı yerel HEAD ile eşleşti. [Kaynak main](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/2f4eabd71b533519098dfee0817d933dbc23d148) · [Geçiş dalı tabanı](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/cb2165f51edcc55176a124f3af8448bef0b0964e)

MIG-01 ve MIG-01B yayımlanmış geçiş dalında, MIG-02 yerel değişikliklerde. Üç MIG-02 becerisinin yerel varlığı, benzersiz metadata, görev ayrımı ve bağlantıları yeniden doğrulandı. İlk deneme, aynı SHA-256 ile arşivlendi: `913dce3eec55a66ff8321ec04631859fd1272d657a141f4f4a6fc0378676feba`. [MIG-02 raporu](MIG-02.md)

## Yürütme ve inceleme

- `task-execution`, bootstrap → yetki → bağlam → kapsam → uygulama → doğrulama → fark → rapor → insan incelemesi → dur akışını tanımlar. Handoff adımlarından rapor ve inceleme sınırını kullanır.
- `start` kanonik kaynak ve çalışma revizyonunu doğrular. Ürün görevlerinde sabitlenmiş kayıt, açık issue ve mevcut bağımlılık kapısı kullanılır. MIG-03 ayrı ve dar kapsamlı geçiş sözleşmesi ister. Kaynak veya yetki çelişkisi uygulamayı engeller.
- `review` başlangıçtaki dosya baytlarını ve indeksi korur, yeni farkı görev kapsamına bağlar ve zorunlu komut sonuçlarını kaydeder. Başarılı yerel kontroller insan onayı bekleyen bir kayıt üretir. `decision` doğru geliştirici ve inceleme kimliğini ister, değişen dosyalarla eski onayı reddeder ve bir incelemeye tek karar makbuzu yazar. `ONAYLA` sonucu ayrı yayın incelemesine aktarılabilir. `DÜZELT` yeni bir diff ve inceleme gerektirir. `REDDET` mevcut işi koruyarak durur.
- Yardımcı bir sandbox veya insan kimliği doğrulayıcısı değildir. Onay ve korumalı kapsam kanıtını insan doğrular. Komutlar yetkili sözleşmeden ve gerçek test kaynaklarından seçilir. Yerel JSON ve makbuzlar checkout dışında tutulur. Komut çıktısı saklanmadığı için komutun içindeki atlanan zorunlu vakalar ayrıca incelenmelidir.

## Kanıt ve kalan sınırlar

- `python -B -m unittest discover -s tests/governance` → **136 test geçti**, 13’ü MIG-03’e özgü. Gerçek geçici Git çalışma ağaçları ve salt okunur GitHub fixture’ları kullanıldı.
- `python -B scripts/governance/task_execution.py start --contract <geçici-sözleşme>` → canlı kaynak ve yerel MIG-02 girdileriyle `TASK_AUTHORIZED`. Bu çalışma bir ürün görevi başlatmadı.
- `python -B scripts/governance/check_docs.py`, `python -B scripts/governance/security_check.py`, `git diff --check` ve bağımlılıksız statik metadata/bağlantı denetimi → **PASS**. Canlı Codex beceri keşfi ve gerçek hosted yürütme **NOT_RUN**.
- `python -B experiments/java-pilot/verify_integrity.py` → çıkış **1**, mevcut `v0-source.json` manifest uyuşmazlığı. Dondurulmuş dosyalar yeniden yazılmadı. MIG-03 testleri bu girdiye bağlı değil. Bu girdiyi zorunlu kılan kontroller ve bunlara bağlı yayın/kabul engeli sürer. [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48)

Görev kaydı, kabul kayıtları, dondurulmuş girdiler ve önceki geçiş çalışmaları korundu. Alperen Enes Yaman, F02-CONTRACT / #11, rotasyon indeksi 2. Tarihsel faz tohumu çalışma zamanı yetki kaynağı değildir. Etkin olay yazıcısı veya faz kilidi servisi gözlenmedi. Yeni olay, kabul veya kilit kaydı üretilmedi. [Kilit ve geçmiş sözleşmesi](../governance/migrations/PHASE_1_HISTORY_AND_LOCKING_ADDENDUM.md)

MIG-04’e aktarılacak kanıt, görev ve geliştirici, depo/dal, canlı kaynak SHA, çalışma HEAD’i, kapsam, kontrol sonuçları, incelenen içerik kimliği ve açık insan kararıdır. Roller ayrı tutulur: atanan sahip, uygulayıcı, PR yazarı, commit yazarları, inceleyen ve insan onaylayan. MIG-04 bu girdileri yayından önce yeniden doğrulamalıdır. Bu oturumda commit, push, PR, merge, kabul veya rotasyon işlemi yapılmadı.
