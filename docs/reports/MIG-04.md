# Project Genesis v3.0 — MIG-04

| Alan | Sonuç |
|---|---|
| Kaynak `main` | `2f4eabd71b533519098dfee0817d933dbc23d148` |
| Dal ve başlangıç HEAD | `chore/1-genesis-v3-phase1` · `1e459c520ca4aaba72ddbfece4d98537e4b48215` |
| Uygulama | Yerel yayın yardımcısı, beceri ve testler hazır. Canlı uçtan uca etkinleştirme `BLOCKED`. |
| Tek komut | İncelenen olağan göreve bağlı `PUSHLA`, uygun adımlarda ikinci onay istemez. |
| Yerel doğrulama | `LOCAL_VERIFIED` · 149 yönetişim testi, geçici Git depoları ve GitHub fixture’ları |
| Hosted doğrulama, yayın, kabul ve kilit | `NOT_RUN` · `NOT_PUBLISHED` · `NOT_ACCEPTED` · `NOT_LOCKED` |

Canlı Git ref’leri yerel başlangıçla eşleşti. Çalışma ağacı temizdi. MIG-01, MIG-01B, MIG-02 ve MIG-03 commit’leri korundu. Ürün rotasyonu ve kabul kayıtları değişmedi.

## Değişiklikler ve çalışma biçimi

- [safe-publish becerisi](../../.agents/skills/safe-publish/SKILL.md), [task-execution](../../.agents/skills/task-execution/SKILL.md) ve [development-handoff](../../.agents/skills/development-handoff/SKILL.md) aynı inceleme kaydını kullanır. [V3 protokolü](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) ve [ekip akışı](../TEAM_WORKFLOW.md) tek komut sınırını kaydeder.
- [Yayın yardımcısı](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/scripts/governance/safe_publish.py) kanonik HTTPS hedefini, canlı tabanı, görev ve kapsamı, inceleme özetini, GitHub hesabını, izinleri ve güvenilen yayın politikasını doğrular. İncelenen yolları commit eder ve ham blob baytlarını karşılaştırır. Bilinen ilgisiz çalışma dosyaları commit dışında kalır. İlgisiz staged değişiklik varsa durur. [GitHub istemcisi](../../scripts/governance/github_api.py) kimlik ve native review durumunu da okuyabilir.
- Aynı SHA’yı yalnızca numaralı özellik dalına force kullanmadan gönderir. Görev için rakip PR’ı reddeder. Doğru PR’ı yeniden kullanır veya açar. Bağımsız içeriğe sahip mevcut PR gövdesini değiştirmez. Gerçek hesapla head’e bağlı onay yorumunu kaydeder. Yönetilen PR gövdesine kanıt bağlantısı ekleyerek onay sonrası güvenilen kapıların yeniden tetiklenmesini sağlar.
- Zorunlu kontrollerin tam head SHA ve GitHub Actions kaynağıyla başarılı olmasını bekler. Onaydan önce başlamış güvenilen kapı koşularını güncel kanıt saymaz. Native review zorunluysa GitHub’ın review kararı `APPROVED` olmalı. GitHub’a gönderilen merge isteği tam head SHA’sını içerir. Birleştirme sonrası PR, merge ebeveynleri, canlı `main` soyu ve uygulanabilir post-merge kontrolleri yeniden doğrulanır.
- Yerel günlük aynı yetkiyle güvenli yeniden denemeye yarar. Push hatası commit’i korur. CI veya merge engeli dalı ve PR’ı korur. CI bekleme süresi dolarsa durum `PUBLISHED_PENDING_CI`. Merge sonrasında kabul eksikse `MERGED_PENDING_ACCEPTANCE`. CLI bekleyen durumlar için çıkış 2, bloke işlem için çıkış 1 ve doğrulanmış mevcut kabul için çıkış 0 döndürür. Süreç arka planda çalışmaya devam etmez.

Olağan otomatik yayın için incelenen dalın başlangıcı doğrulanan `main` ile aynı olmalı. Divergence, başka bir revizyona ait PR veya scope değişikliği yeniden uzlaştırma gerektirir. Korunan bir değişiklik için aynı `PUSHLA` ancak ayrı kapsam kanıtı mevcutsa ve gerçek aktör gerekli sahip yetkisine sahipse kullanılabilir. Yordam, başka bir hesabın onayını temsil etmez.

## Trusted-main geçişi ve bir kerelik yönetici adımı

Canlı `main` kapısı **F02-CONTRACT / #11** ve **Alperen Enes Yaman** eşleşmesini bekliyor. Geçiş dalı **F01-GOV / #1** kapsamına giriyor. `AGENTS.md` ve beceri yolları da eski #1 listesinde yer almıyor. Güvenilen workflow `pull_request_target` üzerinden güncel `main` kodunu çalıştırıyor. Bu dal kendi PR’ına yetki veremez. Eski #38 istisnası ve ADR 0006’nın #45 yetki devri bu aday için kullanılamaz.

1. Önce son aday diff’i ve SHA’yı inceleyin. Proje sahibi Burkay’ın tek kullanımlık kararı depo, hedef `main`, #1/F01-GOV, gerçek PR numarası, kaynak dal, yetkili GitHub aktörü, güvenilen taban SHA’sı, tam head SHA ve tam dosya listesine bağlanmalı. Kayıtta kararın kaynak bağlantısı ve kullanıldıktan sonra geçersiz kalacağı belirtilmeli. SHA veya kapsam değişirse eski karar geçersiz.
2. Mevcut rotasyon/yazar koşulundan ve #1 kapsam dışı dosyalardan gereken dar istisnayı, **adaydan bağımsız güvenilen politika** uygulamalı. Sadece bu kimlik ve diff için izin verilmeli. Ayrı sahip onayı, bağımsız geçiş incelemesi, gerçek önkoşul ve CI kontrolleri korunmalı. Bu istisnayı güvenilen tabana aktaracak mevcut, kontrolleri koruyan bir yönetici yolu doğrulanmadı. Yetkili proje sahibi ve GitHub yöneticisi önce o yolu kayıtlı biçimde tesis etmeli. Bu adım gerçekleşene kadar adayın birleştirilmesi `BLOCKED`.
3. GitHub yöneticisi etkin korumayı ayrıca doğrulamalı. [Klasik koruma önerisi](../../.github/branch-protection.proposed.json) PR, strict güncellik, GitHub Actions uygulamasına bağlı altı kontrol, çözülmüş konuşmalar, yönetici dahil uygulama ve force push/silme yasağını içeriyor. Olağan görevler için onay sayısı sıfır, CODEOWNER ve son-push inceleme zorunluluğu kapalı. Yetkili yönetici, güvenilen korumalı-yol kontrolleri etkinleştirildikten sonra `PUT /repos/caferkilinc/refactoring-ai-generated-code/branches/main/protection` veya eşdeğer GitHub ayar ekranıyla mutabık kalınan kuralı uygulayıp GET ile doğrulamalı. PUT tam yapılandırmayı günceller. Varsa ek etkin korumalar ayrıca uzlaştırılmalı. Geçişin bağımsız incelemesi devam eder.

İnceleme sırasında GitHub dal API’si `protected: false` ve görünür etkin ruleset listesi boş gösterdi. Kimlik doğrulanmış depo sorgusunda `allow_merge_commit: true`, `allow_auto_merge: false` ve mevcut hesabın `admin: false` olduğu görüldü. Ayarlar uygulanmadı. Yayın yardımcısı doğrulanabilir klasik koruma ve GitHub merge-commit desteği ister. İlave ruleset veya okunamayan yönetici ayarı varsa işlem durur. Canlı depoda GitHub auto-merge kapalı olduğu için sınırlı CI beklemesi kullanılır.

## Testler ve bütünlük

- [MIG-03 fixture düzeltmesi](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/tests/governance/test_task_execution.py), geçici Git nesnesini kendisi üretir. Yerel `main`, geçmiş SHA ve derin checkout varsayımları kaldırıldı. `python -B -m unittest discover -s tests/governance -p test_task_execution.py` dış `.git` dizini olmayan ayrı bir kaynak kopyasında da çalıştırıldı. 13 test geçti.
- `python -B -m unittest discover -s tests/governance` · 149 test geçti. 13 MIG-04 testinde geçici Git depoları ve mocked GitHub üzerinden tek komut, kimlik, eski inceleme, kirli çalışma ağacı, güvenli commit/push, tekrarlanan PR, başarısız/eksik/eski CI, review, merge ve kabul tekrarları denetlendi. [MIG-04 testleri](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2f9e05e0df886b250a690122b3369a45fee3fe96/tests/governance/test_safe_publish.py)
- `python -B scripts/governance/check_docs.py`, `python -B scripts/governance/security_check.py`, `git diff --check` ve statik beceri metadata/bağlantı kontrolü uygulandı. Canlı beceri keşfi ve GitHub mutasyonları denenmedi.
- `python -B experiments/java-pilot/verify_integrity.py` · önceden var olan `v0-source.json` manifest uyuşmazlığı sürüyor. Dondurulmuş dosyalar değiştirilmedi. Yardımcı `pilot-checks` sonucunu hem PR hem merge sonrası doğrulamada ister. [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48) ayrı korumalı bakım olarak açık.

## Kabul, geçmiş ve kilit

Merge doğrulandıktan sonra yardımcı mevcut `propose_handoff` kapısıyla kabul adayı ve kanıtı hazırlar. İş sahibi, PR yazarı, commit yazarları, inceleyen ve onaylayan ayrı alanlardır. Doğrulanmamış uygulayıcı `null` kalır. Var olan kabul aynı PR/SHA ile yeniden görülürse `ALREADY_ACCEPTED` olarak işlenir. Yerel JSON çıktısı, kanonik geçmiş kaydı oluşturmaz.

Güvenilen `main` üzerinde yetkili atomik kabul/rotasyon yazıcısı ve etkin faz kilidi servisi bulunmuyor. Bu nedenle yardımcı kabul kaydı yayımlamaz, rotasyon yazmaz veya faz kilitlemez. Tek komutun kabulden kilide kadar otomatik tamamlanması, ayrı yetkili kayıt mekanizması ve bağımsız faz uygunluğu kanıtı sağlanana kadar bloke. Bu oturumda MIG-04 dahil hiçbir yayın işlemi yapılmadı ve MIG-05 başlatılmadı.
