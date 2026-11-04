# Project Genesis v3.0 — Faz 1 geçmiş ve kilitleme eki

**MIG-01B · İnceleme için gereksinim eki**

Bu ek, MIG-01 sonrasında belirlenen kalıcı geçmiş, katkı atfı ve faz kilidi gereksinimlerini kayda geçirir. [Proje hafızası](../../history/PROJECT_GENESIS_PROJECT_MEMORY_2026-11-04.md) ve [faz tohumu](CODEX_NATIVE_PHASE_LEDGER_SEED.json) tarihsel başlangıç verisidir. Görev ve kabul otoritesi, doğrulanan `main` üzerindeki [görev planı](../../../.github/task-plan.json), [kabul kaydı](../../../.github/acceptance.json) ve bunların bağlı GitHub kanıtlarıdır.

## Kalıcı olay geçmişi

Gelecekteki uygulama, önerilen `docs/history/GENESIS_EVENTS.jsonl` yolunda UTF-8, satır başına bir JSON nesnesi içeren ve sonuna yeni olay eklenen bir geçmiş tutmalıdır. Her olay şu alanları taşır:

| Alan | Anlam |
|---|---|
| `event_id`, `event_type` | Kararlı benzersiz kimlik ve olay tipi. Örnek tipler `TASK_ACCEPTED`, `PHASE_LOCKED`, `PHASE_REOPENED`, `CORRECTION_RECORDED`. |
| `subject_type`, `subject_id` | Kayıtlı görev, ürün fazı veya geçiş fazının türü ve gerçek kimliği. |
| `actor_id`, `actor_role` | Olayı gerçekleştiren doğrulanmış kimlik ve o olaydaki rolü. Kayıt giren kişi ile tarihsel aktör ayrıysa bu fark belirtilir. |
| `commit_sha`, `pr`, `evidence` | İlgili tam SHA, depo ve PR numarası veya URL’si, doğrulama bağlantıları. Gerektiğinde kaynak head, CI ve merge SHA’ları ayrı tutulur. |
| `occurred_at`, `recorded_at`, `backfilled` | Olay zamanı, kayda ekleme zamanı, sonradan tarihsel olarak girilip girilmediği. Zamanlar biliniyorsa saat dilimli ISO 8601 kullanılır. |

Eski olayın zamanı bilinmiyorsa `occurred_at: null` yazılır. `recorded_at` gerçek yazma zamanıdır ve olay zamanı yerine geçmez. Kaynağı bulunamayan aktör, PR veya SHA için `null` kullanılır. Tahmini tarih veya kimlik kanıt olarak kullanılmaz. Bir arşiv kaydının eksik alanları, güncel kabul veya kilit işleminin zorunlu kanıtlarını gevşetmez.

## Durumlar ve faz kilidi

| Durum | Tanım |
|---|---|
| `PLANNED` | İş tanımlı, yürütmeye hazır olduğuna dair doğrulama tamamlanmadı. |
| `READY` | Geçerli kapsam ve zorunlu önkoşullar doğrulandı, yürütme başlayabilir. |
| `IN_PROGRESS` | Yetkili kapsamda çalışma başladı. |
| `REVIEW` | İncelenebilir çıktı var ve doğrulama veya yetkili karar bekliyor. |
| `VERIFIED` | İlgili revizyonun zorunlu teknik ve süreç kanıtları doğrulandı. |
| `ACCEPTED` | Yetkili karar ve ilgili bağımsız kanıt kaydı doğrulandı. Görev kabulü tek başına fazı kapatmaz. |
| `LOCKED` | Faz kabul edildi ve kapsamı, kabul kanıtı ile kilit revizyonu ayrı yetkili kayda bağlandı. |
| `BLOCKED` | Eksik veya başarısız kanıt, yetki, bağımlılık veya bütünlük sorunu sonraki geçişi engelliyor. |

Faz kilidi öncesinde doğrulanmış `main` SHA’sı, fazın zorunlu ölçütleri ve görevleri, kabul kayıtları, kaynak revizyonları, PR merge ve soy kanıtı, uygulanabilir zorunlu GitHub CI ve incelemeleri, bağımlılıklar ve varsa dondurulmuş girdilerin bütünlüğü kontrol edilir. Ayrı yetkili kilit kaydı, faz kimliği, tam kilit SHA’sı, karar sahibi ve kanıt bağlantıları içerir. Başarılı bir iş akışı, tek görev kabulü veya bir dalın yayımlanması faz kilidi oluşturmaz.

Yetkili yeniden açma, önceki kilidi ve nedenini referans alan yeni bir olay gerektirir. Sonradan bulunan bütünlük sapması açık risk veya bloke durum olarak kaydedilir. Geçmiş kilit ve kabul kayıtları korunur. Kayıtlar, güncel yetki ve kanıt olmadan silinemez, yeniden açılamaz veya yeni bir revizyona taşınamaz.

## Katkı atfı

| Alan | Kanıt |
|---|---|
| `assigned_owner` | O tarihteki güvenilen görev/rotasyon kaydı. |
| `actual_implementer` | Doğrulanabilir çalışma veya devir kanıtında belirtilen uygulayıcı. |
| `pr_author` | GitHub PR API hesabı. |
| `commit_authors` | İlgili commit’lerin yazarları ve varsa GitHub hesap eşlemesi. |
| `reviewer` | GitHub review veya açıkça tanımlanmış bağımsız inceleme kaydı. |
| `human_approver` | Yetkili insanın kapsam ve revizyona bağlı onayı. Yetki devri ayrıca kaydedilir. |

Bir hesabın birden fazla rolü olabilir. Her rol ayrı kanıtla doldurulur. Örneğin #45’in onay yorumu Cafer’in dar yetki devri kapsamındaki eylemini gösterir. Bu kayıt Burkay’ın GitHub yorumu, bağımsız review veya gelecekteki bir revizyonun onayı olarak yorumlanamaz.

## Tarihsel bütünlük ve idempotent işleme

- Kabul edilen geçmişi yerinde düzeltme. Yeni olay, önceki `event_id` veya kabul anahtarını, düzeltme nedenini, kanıtı ve yetkili kararı referans alır. Görev planı, kabul geçmişi ve dondurulmuş araştırma girdileri, ayrı ve açık yetki olmadan değiştirilemez.
- Görev kabul anahtarı `plan_id:head_sha` olarak kalır. Aynı anahtar tekrar gelirse önceki kayıt döndürülür. Kabul olayı ve rotasyon tekrar yazılmaz. Kabul edilmiş görevin farklı revizyonu korumalı uzlaştırma gerektirir.
- Her fazın yetkili yeniden açma döngüsü başına en fazla bir kilit olayı olabilir. Aynı kilit kaydı tekrarlanırsa yeni olay yazılmaz. Aynı döngü için farklı kilit revizyonu çakışma sayılır. Geri doldurma işlemleri de kararlı olay kimliğiyle tekilleştirilir.
- Gelecekteki yazıcı, kabul, tarihsel olay ve rotasyon değişikliğini tek incelenmiş güncellemede hazırlamalı. Yazımdan önce güncel `main` ve daha önce kullanılan anahtarlar yeniden kontrol edilmeli. Eşzamanlı değişiklikte güncel tabandan doğrulama tekrarlanmalı.

## Zorunlu doğrulama

| Durum | Beklenen sonuç |
|---|---|
| Farklı atanan kişi, uygulayıcı, PR/commit yazarı, inceleyen ve onaylayan | Roller kanıtlarıyla korunur. Bilinmeyen alanlar bilinmiyor kalır. |
| Tam ve güncel kabul kanıtı | Kayıtlı görev, repo/PR, head, gerekli CI, merge soyu, önkoşullar ve yetki doğrulanır. Faz kilidi ayrı değerlendirilir. |
| Eski SHA veya eksik, başarısız ya da atlanan zorunlu CI | İlgili kabul veya kilit reddedilir. |
| Yetkisiz yeniden açma | Mevcut kilit ve geçmiş korunur. İşlem reddedilir. |
| Aynı kabul, kilit veya tarihsel geri doldurma olayı tekrar gelir | Yinelenen olay ve ikinci rotasyon oluşmaz. |
| Yetkili düzeltme ve kapsam denetimi | Önceki kayıtlar erişilebilir kalır. Görev/bağımlılık grafı ve dondurulmuş araştırma girdileri diff ve hash kontrolleriyle korunur. |

## MIG-01 uyumluluğu ve kalan iş

[MIG-01 dalında](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/3421531b530abde42e7d04bfcddcbc87b3993b9c) [v3 protokolü](../PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) ve [gate.py](../../../scripts/governance/gate.py) mevcut. Kod, yetkili geliştirici yorumunu tam revizyon ve kapsama bağlar. Korumalı yol, önkoşul ve CI kontrollerini uygular. `--mode handoff` salt okunur öneri üretir ve mevcut kabulde `ALREADY_ACCEPTED` ile ilerlemeyi kapatır. [Yerel testler](../../../tests/governance/test_codex_authority.py) bu davranışları kapsar.

Olay yazıcısı, faz kilitleme/yeniden açma, rol bazlı olay kaydı, atomik kabul ve rotasyon yazımı, otomatik sonraki prompt ve uçtan uca hosted doğrulama eksiktir. Bu ek, söz konusu davranışların uygulandığı veya geçişin kabul edildiği anlamına gelmez. MIG-01 yayımlanmış çalışma dalında inceleme aşamasındadır. Güvenilen `main` entegrasyonu, yetkili kabul ve GitHub etkinleştirme kanıtı ayrı gerekliliklerdir. Bu ek bir sonraki fazı başlatmaz.
