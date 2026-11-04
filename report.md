# Project Genesis v3.0 — Faz 1 yönetişim geçişi

| Alan | Kayıt |
|---|---|
| Görev | GENESIS-V3-PHASE1 / F01-GOV (#1), korumalı yönetişim hazırlığı |
| Durum | `LOCAL_VERIFIED` (yönetişim) · `PENDING_PUSH_CONFIRMATION` · GitHub etkinleştirmesi `BLOCKED` |
| Kaynak | Kanonik `main` · `2f4eabd71b533519098dfee0817d933dbc23d148` |
| Yerel dal | `chore/1-genesis-v3-phase1` |
| Geliştirici | Burkay Çakar, yerel Windows kullanıcısı `laptop-1ebli599\burkay`. Bu işlemde GitHub hesabıyla kimlik doğrulanmadı. |
| Ortam | Windows 11 26H2, derleme 26300.9711 · PowerShell 7.6.5 · Git for Windows 2.56.0.windows.4 · Python 3.14.5 |
| Aktif ürün görevi | Alperen Enes Yaman (`Yaman-A-E`) / F02-CONTRACT / #11. Faz 1 bir rotasyon turu kullanmaz. |

Temiz, tek worktree'deki `main`, `origin/main` ve doğrudan GitHub sorguları aynı SHA'yı verdi. Bu tabandan ayrı yerel dal açıldı. Eski kabul raporu kaynak commit'te korunur. [Kaynak commit](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/2f4eabd71b533519098dfee0817d933dbc23d148) · [Önceki rapor](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/2f4eabd71b533519098dfee0817d933dbc23d148/report.md)

## Yetki ve kontrol değişiklikleri

| Tür ve konum | Eski kural → Faz 1 | Güvenlik, test ve uyumluluk |
|---|---|---|
| İnsan iş akışı · `AGENTS.md`, el değiştirme becerisi, katkı ve ekip kılavuzları, PR/issue şablonları | Dış orkestratör yetkilendirir ve her olağan PR Burkay'ın onayını ister → güvenilen kayıt tek aktif görev/sahibi belirler, aktif geliştirici sınırlandırılmış yürütmeyi ve gözden geçirdiği revizyonun yayımlanmasını açıkça yetkilendirir. | Sınırlı görev sözleşmesi, tek uygulama sahibi, bağımsız kabul ve korumalı işlerde ayrı sahip kararı sürer. Yerel belge bağlantıları denetlendi. |
| İnsan iş akışı · v2.1 protokolü, ADR 0004/0006, SRS §9 ve son onay, mimarinin rotasyon bölümü, tarihli durum/yol haritası | Dış orkestrasyon, tek onay yetkisi ve sonraki prompt derleme kilidi → etkinleştirmeden sonra kanonik v3 protokolü. Codex, bağımsız kabulden sonra doğrulanmış kaynaklarla hazırlık promptu taslağı üretebilir. | Tarihsel kayıtlar ile ürün SRS/mimari metinleri korundu. Sahip, etkinleştirmede bu metinlerdeki eski yürütme hükümlerinin v3 ile uzlaştırılmasını açıkça onaylamalı. Faz 1 prompt üretmedi. |
| Makine · `gate.py`, `dependency-gate.yml` | Her olağan PR için SHA'ya bağlı sahip yorumu → doğrulanmış GitHub yorum yazarı, aktif geliştirici ve PR yazarı eşleşir. Onay tam görev, kanonik repo, dal, kaynak SHA ve `merge` kapsamına bağlıdır. | Fork, yanlış geliştirici/görev/revizyon/kapsam ve eksik onay reddedilir. Korunan yollar, yeniden adlandırmanın iki tarafı ve iş akışı değişiklikleri ayrı sahip onayı gerektirir. Görev kapsamı, yerel bağımlılık kayıtları, canlı bağımlılık grafı, güvenilen taban ve zorunlu CI kontrolleri sürer. Kodla ifade edilmeyen korumalı niyeti insan incelemesi değerlendirir. |
| Makine · kabul kaydı ve `gate.py --mode handoff` | Operasyonel kabul dış orkestratöre bağlı → birleştirme kaydını, CI/bağımlılıkları ve `main` soyunu denetleyen salt okunur öneri. | Kabul/rotasyon yazımı yok. `plan_id:head_sha` tekrarında ikinci ilerleme yok. #44'ün sahip onayı ve #45'in ADR 0006 istisnası tarihsel doğrulamada korunuyor. |
| GitHub · `main` koruma ayarları, CODEOWNERS, gerekli iş adları | PR yazarının yorumu, GitHub bağımsız PR incelemesinden ayrı kanıt. | GitHub izinleri, CODEOWNERS ve önerilen kural dosyası değişmedi. Uygulanan kurallar ve gerçek hosted koşular yerel testten bağımsız denetlenmeli. |

Durumlar ayrı değerlendirilir. `DEVELOPER_APPROVED` onay kanıtını, `LOCAL_VERIFIED` yerel sonuçları, `HOSTED_VERIFIED` zorunlu GitHub kontrolleri ve incelemelerini, `MERGED` GitHub birleştirmesi ve Git soyunu, `HANDOFF_ACCEPTED` ise bağımsız incelemeden sonra güvenilen `main` üzerindeki kabul kaydını ifade eder.

## Canlı durum ve açık PR uyumluluğu

- F00-PLAN (#8, PR #44) ve F00-V0 (#9, PR #45) tamamlandı. Kabul kayıtları ve özgün CI/onay kanıtları salt okunur GitHub API sorgularıyla yeniden doğrulandı. Her iki merge commit'i kaynak `main`in atası. #9 yeniden işlendiğinde `ALREADY_ACCEPTED`, `advance: false` döndü. [PR #44](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/44) · [PR #45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45)
- #11 açık. Güvenilen kayıt Alperen'i aktif geliştirici olarak belirliyor. Canlı önkoşul #8. Rotasyon sırası Burkay → Cafer → Alperen → İsmail → Taha ve güncel indeks 2. [Issue #11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11)
- #43, `22fc78218fd3c43b727e7f051117646af70f3916`, açık ve iki UML görselleştirme dosyasını değiştiriyor. #48, `2f0d21e9c289abd783855c6d4687b38c388bcc8b`, açık ve korunan SRS, v2.1 protokolü ve dondurulmuş pilot dosyalarını da değiştiriyor. İncelenen dosya listeleri Faz 1 dosyalarıyla kesişmiyor. Yeni politika bu açık PR'lara görev, rotasyon veya kapsam istisnası vermez. [PR #43](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/43) · [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48)

## Doğrulama

| Komut / kanıt | Sonuç |
|---|---|
| `git status --porcelain=v1 --branch --ignored=matching -uall`, `git rev-parse`, `git remote -v`, `git worktree list --porcelain`, `git config --show-origin`, `git ls-remote --exit-code origin refs/heads/main`, GitHub ref API | PASS · Kimlik, başlangıç temizliği, upstream, tek worktree, yerel `core.autocrlf=input` ve canlı kaynak SHA doğrulandı. Ek fetch veya entegrasyon gerekmiyordu. |
| `python -B -m unittest discover -s tests/governance -v` | PASS · 123 test. Geçerli olağan onay, eksik/yabancı/eski/yanlış görev onayı, eksik/başarısız CI, izinsiz korumalı değişiklik, eski kabul ve tekrar devri kapsandı. |
| `python -B scripts/governance/check_docs.py`, `python -B scripts/governance/security_check.py`, `git diff --check` | PASS · Belge bağlantıları, depo hijyeni ve diff. |
| Beceri frontmatter ve yeni dosyalarda satır sonu/boşluk kontrolü | PASS · Yerel Python kontrolleri. Standart beceri doğrulayıcısı, PyYAML bulunmadığı için NOT_RUN. |
| `git ls-tree`, `git hash-object --no-filters`, `git ls-files --eol` ve korunan yollarda `git status` | PASS · 45 korunan dosya kaynak Git blob'uyla byte düzeyinde aynı. SRS, mimari, güvenlik, tarihsel kararlar, görev planı, kabul, CODEOWNERS, önerilen koruma ve araştırma dosyaları dahil. |
| Canlı salt okunur `verify_acceptance` / `propose_handoff`, `git merge-base --is-ancestor` | PASS · #8/#9 tarihsel kabul ve kaynak soy doğrulaması. #9 tekrarında ilerleme yok. |
| `python -B experiments/java-pilot/verify_integrity.py` | FAIL · Faz 1 düzenlemelerinden önce de `v0-source.json` SHA-256 uyuşmazlığı vardı. Manifest yan dosyası `1650a915ea6516e52ac27c1a4c98a11d0ddd62155f41ec6a21835b0195311376`, dosyanın gerçek özeti `0ca386a2a438162a5c6ce9d63100411e303016f674787be7a462da9d18d079c9`. Korunan dosyalar değişmedi. |
| Faz 1 GitHub Actions ve yeni kural denemeleri | NOT_RUN · Yerel dala ait hosted koşu yok. |

## GitHub etkinleştirme ve yayın kapısı

Herkese açık `GET /branches/main` yanıtı `protected: false` ve durum kontrolü listesini boş gösterdi. `GET /rules/branches/main` ve `GET /rulesets` boş döndü. Ayrıntılı klasik koruma uç noktası HTTP 401 verdi. Bu oturumda GitHub yönetici yetkisi doğrulanmadı ve hiçbir ayar değiştirilmedi. [Dal API kaydı](https://api.github.com/repos/caferkilinc/refactoring-ai-generated-code/branches/main)

Yetkili yönetici, `main` için etkin bir PR koruma kuralı oluşturmalı. [Önerilen koruma dosyasındaki](.github/branch-protection.proposed.json) beş kontrolü zorunlu yapmalı (`governance-tests`, `documentation-checks`, `security-checks`, `dependency-gate`, `merge-readiness`). GitHub Actions kaynağını doğrulamalı, dalın güncel olmasını, bir bağımsız CODEOWNER incelemesini, eski incelemelerin düşmesini, görüşmelerin çözülmesini ve yönetici dahil kuralların uygulanmasını zorunlu tutmalı. Force push ve dal silme kapalı olmalı. Uygulanabilir ek iş kontrolleri görev kapısında zorunlu kalır. [GitHub koruma ayarları](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Korumalı geçiş için Burkay'ın açık ve kayda alınmış sahip kararı, ayrıca yayın kapsamına ilişkin geliştirici onayı gerekir. Canlı v2 kapısı Faz 1 dalını yetkilendirmez. #1 aktif ürün görevi değildir ve `AGENTS.md` ile beceri mevcut #1 yol listesinde yoktur. Güvenilen tabanda, ayrı onaylı geçiş yolu repo, #1, dal, geliştirici, kesin revizyon ve bu iki yol dahil değişiklik kapsamını sınırlamalı. Faz 1 PR'ının kendi kodu yetki kaynağı olamaz. Uygun güvenilen geçiş yolu yoksa birleşme bloke kalır. Etkinleştirmeden sonra yöneticinin gerçek PR'da olumlu/olumsuz onay ve zorunlu CI denemelerini doğrulaması gerekir.

## Dosyalar, geri dönüş ve sonraki faz

- Yetki ve testler · `scripts/governance/gate.py`, `tests/governance/test_codex_authority.py`, `tests/governance/test_audit_regressions.py`
- GitHub şablonları ve kapı · `.github/ISSUE_TEMPLATE/task.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/dependency-gate.yml`
- Protokol ve çalışma talimatları · `docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md`, `AGENTS.md`, `.agents/skills/development-handoff/SKILL.md`, `CONTRIBUTING.md`, `README.md`, `docs/TEAM_WORKFLOW.md`, `docs/DEPENDENCY_MANAGEMENT.md`, `docs/DEVELOPMENT_ROADMAP.md`, `report.md`

Yerel değişiklikleri inceleme dalında tutarak önceki güvenilen `main` kullanılabilir. Yayımlanmış bir geçişin geri alınması ayrı sahip yetkili, incelenmiş bir revert PR'ı ve aynı CI kontrollerini gerektirir. Kabul kayıtları ve rotasyon geçmişi korunur. Faz 2, ayrıca yetkilendirildiğinde görev sözleşmesi ile doğrulama kanıtı akışını tamamlamalı. Otomatik yayımlama, kabul yazımı veya sonraki görev promptu bu fazda çalıştırılmadı.
