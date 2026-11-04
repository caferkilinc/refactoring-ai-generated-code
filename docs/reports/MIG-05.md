# Project Genesis v3.0 — MIG-05

| Alan | Durum |
|---|---|
| Migrasyon | `MIG-05` |
| Kesinti kurtarma | Kaydedilmiş MIG-05 yordamları ve testleri yerinde doğrulandı. Eksik ilk post-migrasyon handoff koşulu eklendi. |
| Doğrulanan kaynak `main` | `2f4eabd71b533519098dfee0817d933dbc23d148` |
| Çalışma dalı | `chore/1-genesis-v3-phase1` |
| Yerel HEAD ve canlı migrasyon ref’i | `1e459c520ca4aaba72ddbfece4d98537e4b48215` |
| Kabul yazıcısı | Tam revizyona bağlı, tek Git değişikliği için kabul, rotasyon ve geçmiş paketi hazırlar. |
| Geçmiş yazıcısı | UTF-8 JSONL sonuna ekler. Kimlik çakışmalarını reddeder. Düzeltme önceki olayı korur. |
| Faz kilidi | Kanonik olaylardan türetilir. Ürün ve migrasyon ayrı değerlendirilir. Kilitleme ve yeniden açma sahip kararına bağlıdır. |
| Sonraki adım | Güvenilen kaynaklardan durum ve hazırlık promptu üretir. Taslak canlı kaynaklara karşı yeniden doğrulanabilir. |
| Tek komut | `PUSHLA` incelemeye bağlı normal yayın akışını başlatır. Doğrulanan merge kabul paketini tetikler. |
| Alperen ve frozen kapsamı | `PENDING_PROTECTED_RECONCILIATION` · Gelecekteki çalışma için `Yaman-A-E` kaydedildi. Kesin görev henüz yetkilendirilmedi. |
| Ürün rotasyonu | `F02-CONTRACT / #11`, Alperen Enes Yaman (`Yaman-A-E`), indeks 2. Koşullu sonraki geliştirici `ismail-cevik`. |
| Tarihsel uyumluluk | `F00-PLAN / #8 / PR #44` ve `F00-V0 / #9 / PR #45` önceki kayıtları korundu. |
| Pilot bütünlüğü | `FAIL` · `experiments/java-pilot/manifests/v0-source.json` manifest hash uyuşmazlığı. |
| Korumalı ürün girdileri | Kanonik görev, kabul ve dondurulmuş pilot girdileri değişmedi. |
| Güvenilen main geçişi | `REQUIRES_AUTHORIZED_MIGRATION` · Aday kendi geçiş yetkisini oluşturamaz. |
| Yerel doğrulama | `LOCAL_VERIFIED` · 155 yönetişim testi geçti. Pilot bütünlük sonucu ayrı olarak `FAIL`. |
| GitHub doğrulaması | Canlı ref ve geçmiş kanıtı salt okunur incelendi. MIG-05 hosted yürütme `NOT_RUN`. Klasik koruma ayrıntıları `UNKNOWN`. |
| Yayın ve kilit | `NOT_PUBLISHED` · `NOT_LOCKED`. |

## Kabul, geçmiş ve faz kayıtlarının hazırlanması

[Kabul yardımcısı](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/lifecycle.py) kanonik Git ref’i ile GitHub ref’ini karşılaştırır. Güvenilen tabandan kayıtları okur ve çalıştırılan v3 yordamını doğrular. PR kimliği, head, merge ebeveynleri, main soyu, merge öncesi yetkili geliştirici yorumu, koruma yapılandırması, gereken Actions kontrolleri ve önkoşulları denetler. Aynı kabul anahtarı doğrulandığında dosya güncellemesi üretmez. Çakışan PR ya da head ayrı korumalı uzlaştırma gerektirir.

1. [Yayın yardımcısı](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/safe_publish.py) post-merge kontrolleri tamamlanınca `acceptance_transaction` üretir. Paket `.github/acceptance.json`, `.github/task-plan.json` ve `docs/history/GENESIS_EVENTS.jsonl` için tam UTF-8 içerik ve bir işlem özeti taşır. Çıktıyı çalışma ağacı dışında saklayın. Güvenilen taban değişirse güncel ref ve kayıtlarla yeniden hazırlayın.
2. Mevcut plan tek uygun açık ardıl görev veriyorsa onu kullanın. Birden çok uygun görev varsa proje sahibinin birleştirilmiş PR’daki tam `GENESIS-NEXT-TASK: <REPO> <MAIN_SHA> <TASK_HEAD_SHA> <NEXT_TASK_ID>` yorumu ve `--next-task` gereklidir. Yerel rapor ve issue assignee yetki kaynağı olarak kullanılmaz.
3. Bağımsız doğrulayıcı paket ve kabul kanıtlarını inceler. Ayrı korumalı kabul PR’ı için yetkili operatör aynı üç içeriği beklenen `main` üzerinde tek commit olarak hazırlar. Gönderimden hemen önce aşağıdaki doğrulama komutunu ilk paketin aynı hazırlama zamanı ve parametreleriyle çalıştırır. Yardımcı revizyonu, yolları, Git blob baytlarını ve tabanı yeniden denetler. Adayın yayın yetkisi, owner kararı ve bağımsız inceleme korumalı PR yolunda ayrıca doğrulanır.

```text
python -B scripts/governance/lifecycle.py --expected-main MAIN_SHA --recorded-at ORIGINAL_PROPOSAL_TIME --verify REVIEWED_TRANSACTION.json --candidate CANDIDATE_SHA accept --pr PR_NUMBER --head TASK_HEAD_SHA --base TASK_MERGE_FIRST_PARENT
```

`--verify` ve `--candidate` olmadan komut yeni inceleme paketi hazırlar. `ORIGINAL_PROPOSAL_TIME` paket olaylarındaki `recorded_at` değeridir. Komut depo kaydını doğrudan yazmaz. Ayrı ve güvenilen korumalı PR yolu sağlanana ve işlem `main`e girene kadar durum `MERGED_PENDING_ACCEPTANCE`. Aynı olağan ürün yayını için geliştiriciden ikinci bir `PUSHLA` istenmez.

Olay dosyası ilk yetkili işlemde oluşur. Birleştirme aktörü, atanmış geliştirici, uygulayıcı, PR yazarı, commit yazarları, native inceleyen ve insan onaylayan ayrı tutulur. Doğrulanmış uygulayıcı atfı bulunmazsa değer `null`. Geçmiş kabul kayıtlarına geriye dönük olay eklenmedi. Yazıcı, başlangıç ve yerel doğrulama dahil sözleşmedeki olay kategorilerini tanır. Otomatik kabul hazırlığı GitHub’dan doğrulayabildiği onay ve merge olaylarını, ardından entegrasyona bağlı kabul ve rotasyon olaylarını hazırlar.

Faz kilitlerinin operasyonel kaynağı aynı olay dosyasıdır. Her ürün fazı için o faza kayıtlı görevler zorunlu kabul edilir. Kanonik kabul, bağımlılıklar, merge soyu ve doğrulanan `main` üzerindeki yönetişim, dokümantasyon, güvenlik ve pilot kontrolleri aranır. Yetkili sahip kararı tamamlanan ölçütleri, belge kanıtını ve ek açık engellerin incelendiğini bağlamalıdır. `phase lock` işlemi için `--evidence` bu incelemenin HTTPS kanıtıdır. Komut, ilgili issue’da beklenen `GENESIS-PHASE-DECISION` işaretini bildirir. Yeniden açma için `phase reopen`, güncel kilit, ayrı sahip kararı ve gerekçe ister. `phase migration-accept` ise #1’deki ayrı karara, doğrulanan migrasyon PR’ına ve önceki migrasyonların kanonik kayıtlarına bağlıdır. Bu işlem ürün rotasyonuna dokunmaz. Kilit kaydındaki zaman sahip kararının zamanıdır. Kilit, kayıt güvenilen `main`e girdikten sonra yürürlüğe girer.

`correct --event EVENT_ID --reason REASON --evidence URL` mevcut olayı değiştirmeden, onunla ilişkili issue’daki `GENESIS-HISTORY-CORRECTION` kararıyla düzeltme paketi hazırlar. Faz ve düzeltme paketleri için de aynı taban ve aday doğrulaması kullanılır.

## Durum ve sonraki prompt

[Durum ve prompt yordamı](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/next_step.py) tamamlanmamış görevleri ve eksik önkoşullarını, önceki kanonik kabulü, PR’ı, doğrulanabilen katkıyı, ürün kilitlerini, migrasyon durumunu ve koşullu sıradaki geliştiriciyi gösterir. [Next-step becerisi](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/.agents/skills/next-step/SKILL.md) güncel ve etkin politikayı, son kabulü, yeni görevin kanonik sırasını, GitHub bağımlılıklarını ve pilot koşulunu denetleyen taslağı kullanır. Taslakta `main` SHA ve görev, kabul, politika, SRS ve mimari blob kimlikleri bulunur. `validate` çıktıyı taze kanıttan yeniden oluşturup bayt düzeyinde karşılaştırır. Arşiv yolu `docs/handoffs/<TASK-ID>/NEXT_STEP_PROMPT.md`. Taslak hazırlığı görev yürütme yetkisi vermez.

### Alperen’in gelecekteki frozen handoff’u

Sahibin yeni sıralama niyeti, [korumalı geçiş kaydında](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/docs/governance/migrations/POST_MIGRATION_HANDOFF.json) Alperen Enes Yaman (`Yaman-A-E`) için beklemede. `reconciled_task_id` ve `reconciliation_evidence` başlangıçta boştur. Etkin v3 ve MIG-01–05’in kanonik kabulü doğrulandıktan sonra yetkili sahip ile bağımsız doğrulayıcı güncel planı, bağımlılıkları ve pilot onarım kanıtını incelemeli, kesin kapsamı ve kayıtlı görevi korumalı yoldan karara bağlamalıdır. Sonraki prompt bu kararı ve ilgili Git blob kimliğini okur. Mevcut aktif atama farklıysa uzlaştırma gerekir. Onarım için korumalı manifest değişikliği gerekiyorsa ayrı kapsam ve yetki yolu geçerlidir.

Canlı atama hâlâ `F02-CONTRACT / #11` ve Alperen. Bugünkü kayıt bu görevi frozen çalışması olarak tanımlamıyor. [F00-V0](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) kabul edilmiş, [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48) açık. Bu iki kanıt yeni bir görev kimliği veya yeniden açma yetkisi sağlamıyor. Yordam, bağımlılık ve diğer yetki koşullarını doğrulamadan prompt üretmez. Doğrulanan frozen handoff kabul edildikten sonra niyetin karşılandığı kanonik kabulden türetilir.

## Güvenilen main geçişi ve bir kerelik yönetici işlemi

Canlı kapı [F02-CONTRACT / #11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) ve Alperen’i bekler. Migrasyon [F01-GOV / #1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) kapsamındadır ve tarihi #1 yol listesinde bulunmayan dosyalar içerir. `pull_request_target` kapısı politikayı güvenilen tabandan çalıştırır. PR #38 bootstrap istisnası ve PR #45’e özel yetki devri bu adaya uygulanmaz.

1. Proje sahibi, ayrı korumalı kararında depo, hedef, gerçek PR numarası, #1, yetkili aktör, kaynak dal, güvenilen taban SHA, incelenen tam head SHA ve tam diff kapsamını bağlamalıdır.
2. Mevcut kapıyı koruyan yönetici yolu doğrulanmadığı için yetkili GitHub yöneticisi ve proje sahibi, adaydan bağımsız güvenilen politika üzerinden bir kerelik dar aktivasyon yolunu tesis etmelidir. Bu yol, yalnızca kayıtlı aday için aktif görev/yazar ve gerekli kapsam farkını karşılamalıdır. Bağımsız inceleme, bağımlılık, teknik kontroller ve mevcut ürün kayıtları korunmalıdır. Ayrı korumalı kabul ve faz PR’larının yetki yolu da güvenilen politikada açıkça tanımlanmalıdır. Bu iki yol kurulana kadar otomatik kanonik yazma bloke.
3. Yönetici gerçek dal korumasını doğrular ve uygulanabilir kuralları etkinleştirir. MIG-04’ün önerdiği düzen strict PR güncelliği, Actions uygulamasına bağlı altı kontrol, yönetici dahil koruma, konuşma çözümü ve force push/silme yasağını içerir. Koruma önerisinin yayınlanması hosted ayarı kendiliğinden değiştirmez. [MIG-04 aktivasyon kanıtı ve klasik koruma önerisi](MIG-04.md)

Pilot uyuşmazlığı bağımsız yayın engelidir. PR #48 açık ve birleştirilmemiştir. Başarılı onarım için güvenilen `main` üzerinde geçerli pilot kanıtı gerekir. [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48)

## Kurtarma ve doğrulama kapsamı

Kurtarma öncesi tek çalışma ağacı, boş index ve bekleyen Git işlemi olmadığı doğrulandı. MIG-01 ve MIG-01B ile MIG-02/MIG-03’ün mevcut üç commit’i korundu. MIG-04’ün yerel yayıncı, beceri, test ve raporu saklandı. Çakışan yayıncı, beceri, v3 protokolü ve fixture yollarına yalnızca MIG-05 entegrasyonu eklendi.

Başlangıçta 149 yönetişim testi geçti. Uçtan uca test, geçici Git deposunda yetkili görevden yerel doğrulama ve `PUSHLA` ile sahte GitHub merge’üne, ardından üç dosyalı kabul paketi, tek rotasyon ilerlemesi, faz kararı ve yeni prompt doğrulamasına uzanır. Negatif kapsam yanlış görev veya geliştirici, eksik önkoşul, eski SHA, onay eksikliği, değişen diff, başarısız yerel doğrulama, eski veya başarısız hosted CI, yanlış PR, geçersiz merge, tekrar ve çakışma, hareket eden `main`, yetkisiz yeniden açma, eksik faz, tutarsız rotasyon ve eski prompt kanıtını içerir. Gerçek GitHub merge’ü, kabul, rotasyon, kilit veya ürün promptu çalıştırılmadı. [MIG-05 testleri](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/tests/governance/test_lifecycle.py)

Kanonik kayıtlar ve dondurulmuş girdiler dahil 14 dosyanın ham baytları güvenilen `main` ile eşleşti. Tarihsel #8 ve #9 issue’ları tamamlanmış, PR #44 ve #45 birleştirilmiş, kayıtlı head’ler eşleşmiş ve merge commit’leri `main` soyunda. #44 sahip onayı ile #45’in ADR 0006 kapsamındaki yetki devri yorumu ve göreve özgü kontroller doğrulandı. Canlı `main` API’si `protected: false` döndürdü ve görünür etkin ruleset bulunmadı. Klasik koruma ayrıntı isteği HTTP 401 döndürdü. [PR #44](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/44) · [PR #45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45) · [Başarısız main pilot kontrolü](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41767254537/job/126368411769)

| Kontrol | Sonuç |
|---|---|
| `python -B -m unittest discover -s tests/governance` | `PASS` · 155 test, 99,093 saniye. Altı MIG-05 testi başarılı. |
| `python -B scripts/governance/check_docs.py` | `PASS` |
| `python -B scripts/governance/security_check.py` | `PASS` |
| `git diff --check` ve yerel yeni dosya boşluk kontrolü | `PASS` |
| Beceri metadata ve yerel bağlantı kontrolü | `PASS` · Statik kontrol. |
| `python -B experiments/java-pilot/verify_integrity.py` | `FAIL` · Önceden var olan `v0-source.json` manifest hash uyuşmazlığı. |
| MIG-05 canlı GitHub CI ve yürütme | `NOT_RUN` · Güvenilen aktivasyon ve pilot engeli devam ediyor. |

## MIG-05 kapsamındaki dosyalar

- Eklenenler · [lifecycle.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/lifecycle.py), [next_step.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/next_step.py), [next-step becerisi](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/.agents/skills/next-step/SKILL.md), [POST_MIGRATION_HANDOFF.json](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/docs/governance/migrations/POST_MIGRATION_HANDOFF.json), [test_lifecycle.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/tests/governance/test_lifecycle.py) ve bu rapor
- Değişenler · [safe_publish.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/safe_publish.py), [gate.py](../../scripts/governance/gate.py), [task_execution.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/task_execution.py), [safe-publish becerisi](../../.agents/skills/safe-publish/SKILL.md), [v3 protokolü](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) ve [test_safe_publish.py](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/tests/governance/test_safe_publish.py)
