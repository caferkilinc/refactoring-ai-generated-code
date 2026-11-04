# Project Genesis — 4 Kasım 2026 proje hafızası

**HISTORICAL_SNAPSHOT** · 2026-11-04 (Europe/Istanbul)<br>
**Proje:** Refactoring AI-Generated Code, Engineering Design II<br>
**Depo:** [caferkilinc/refactoring-ai-generated-code](https://github.com/caferkilinc/refactoring-ai-generated-code)<br>
**Kaynak:** [doğrulanan `main` · `2f4eabd71b533519098dfee0817d933dbc23d148`](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/2f4eabd71b533519098dfee0817d933dbc23d148)

## Kimlik ve onaylı kapsam

Proje, işleme yetkisi verilen kaynak kodda güvenli ve ölçülebilir refactoring yapmayı hedefler. ZIP, klasör veya snippet girdisinden değişmez V0 alınır. Dil ve kalite analizi, deterministik güvenlik taraması ve yalıtılmış başlangıç testleri kanıt üretir. Kullanıcı önce uygun bulguları, sonra doğrulanmış yamaları seçer. Sistem aday yamaları ayrı çalışma kopyalarında doğrular ve seçilen yamaların birleşimini yeni bir V0 kopyasında yeniden test eder. Çıktılar final ZIP, önce/sonra ölçümleri, HTML/PDF raporları ve geçmişi içerir.

İlk teslim P0 kapsamı Java, Python, JavaScript, TypeScript, C#, Go, C++ ve gerçek yerel Falcon-Mamba 7B incelemesini kapsar. Hedef mimari, FastAPI çekirdeği, iş kuyruğu ve yalıtılmış worker’lar, ortak ara temsil (CIR) ve LanguageAdapter sözleşmeleri, kanıta dayalı analiz, kontrollü yama üretimi ve React arayüzünü tanımlar. İki ürün onayı GitHub geliştirme onaylarından ayrıdır. Onaylanmış gereksinimler, çalışan özellik veya sürüm kanıtı sayılmaz. [Türkçe SRS v0.4.0](../SRS.md) · [İngilizce SRS v0.4.0](../SRS_EN.md) · [Mimari](../ARCHITECTURE.md)

## Tarihsel kaynak anlık görüntüsü

Depo kimliği ve kaynak SHA, Git uzak ref sorgusu ve GitHub dal API’si ile eşleştirildi. [Görev kaydı](../../.github/task-plan.json), [kabul kaydı](../../.github/acceptance.json), [AGENTS.md](../../AGENTS.md), [yol haritası](../DEVELOPMENT_ROADMAP.md), [proje durumu](../PROJECT_STATUS.md), [ekip iş akışı](../TEAM_WORKFLOW.md), ADR’ler ve [Cafer → Alperen devir kaydı](../handoffs/F00-V0-to-F02-CONTRACT.md) incelendi. [Kaynak `main` raporu](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/2f4eabd71b533519098dfee0817d933dbc23d148/report.md) ile [MIG-01 dalının raporu](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/3421531b530abde42e7d04bfcddcbc87b3993b9c/report.md) farklı revizyon ve iş kapsamlarını anlatır.

Bir kayıt için GitHub’dan doğrulanan durum, ilgili kaynak SHA ve kontrol koşusuyla birlikte okunur. Tarihli belge veya raporlar geçmişte kaydedilen durumları açıklar. Gelecek aşamalar ve teslim hedefleri plan olarak kalır. Sohbetten aktarılan fakat doğrudan doğrulanamayan yetki veya kaynak erişimi beyanları `REPORTED`, kanıtsız alanlar `UNKNOWN` olarak değerlendirilir. Bu belge güncel görev verme yetkisi taşımaz.

## Ekip ve rotasyon

| İndeks | Geliştirici | GitHub |
|---:|---|---|
| 0 | Burkay Çakar | `cakarburkayy` |
| 1 | Cafer Tayyar Kılınç | `caferkilinc` |
| 2 | Alperen Enes Yaman | `Yaman-A-E` |
| 3 | İsmail Çevik | `ismail-cevik` |
| 4 | Taha Uğur Toyran | `tahaugurtoyran` |

İndeks 4’ten sonra Burkay’a dönülür. Tek aktif uygulama sahibi, doğrulanmış `main` üzerindeki `sequential_execution` alanından belirlenir. Issue assignee’leri ve uzmanlık alanları yetkilendirme kaynağı değildir.

## Planlama geçmişi

Anlık görüntüde **34 teknik görev ve 69 önkoşul bağlantısı** bulunuyordu. Önceki 31 görev ve 54 bağlantı korunarak C#, Go ve C++ görevleri ile 15 bağlantı eklendi. Sayılar sabitlenmiş görev kaydından yeniden hesaplandı. GitHub’daki tarihsel doğal bağımlılık denetimi ikinci denemede başarılıydı. Her bağlantının tanımı ve güncel durumu için kanonik kayda ve GitHub önkoşullarına bakılır. [Graf denetimi](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/40518968864/attempts/2)

| Araştırma iş paketi | Ürün fazları ve teknik görev kimlikleri |
|---|---|
| İP1 · Deney temeli ve platform sözleşmeleri ([#2](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/2)) | F00: `F00-PLAN`, `F00-V0`; F01: `F01-GOV`, `F01-ENV`; F02: `F02-CONTRACT`, `F02-STATE`; F03: `F03-INPUT` |
| İP2 · Dil çekirdeği ve başlangıç kalite/davranış ölçümü ([#3](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/3)) | F04: `F04-JAVA`; F05: `F05-QUALITY`; F06: `F06-SANDBOX`, `F06-TESTS` |
| İP3 · Güvenlik inceleme hattı ve Local AI ([#4](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/4)) | F07A: `F07A-SCAN`; F07B: `F07B-PILOT`, `F07B-LOCAL` |
| İP4 · İlk onay ve bağımlılığa duyarlı paralel refactoring ([#5](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/5)) | F08: `F08-UI`, `F08-INTEGRATE`; F09: `F09-CONTEXT`, `F09-SCHED`; F10: `F10-PATCH` |
| İP5 · Kanıta dayalı doğrulama ve nihai sürüm ([#6](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/6)) | F11: `F11-VALIDATE`, `F11-RETRY`; F12: `F12-REVIEW`, `F12-FINAL`; F13: `F13-BASIC`, `F13-ADV` |
| İP6 · Çok dilli genişleme ve deneysel değerlendirme ([#7](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/7)) | F14: `F14-PY`, `F14-JSTS`, `F14-MIX`, `F14-CS`, `F14-GO`, `F14-CPP`; F15: `F15-P0`, `F15-EXPERIMENT`, `F15-HANDIN` |

## Kabul edilmiş işler

| Görev ve tarihsel durum | Geliştirici ve PR | Kabul edilen kaynak SHA | Merge SHA | Kabul CI SHA |
|---|---|---|---|---|
| `F00-PLAN` [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) · `VERIFIED_COMPLETE` | Burkay Çakar · [#44](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/44) | `a281caec295487b78371bac1e106cb378fa64bba` | `ac321cb43fdea3f6b64bb1631de8daca8cf1d229` | `a281caec295487b78371bac1e106cb378fa64bba` |
| `F00-V0` [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) · `VERIFIED_COMPLETE` | Cafer Tayyar Kılınç · [#45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45) | `d923134da4f9f5a2ab55a5f51fbf9415ff717262` | `fdd573286834fe15c1ac1c0d51db4ed9b0015db7` | `fdd573286834fe15c1ac1c0d51db4ed9b0015db7` |

- **F00-PLAN.** Araştırma kapsamı, kaynak/deney protokolü ve kanıt temeli kayda geçti. Tarihsel uygulayıcı ve atanan kişi Burkay’dı. GitHub, PR yazarını ve iki kaynak commit’in hesap bağlantısını `cakarburkayy` olarak gösterdi. Bu hesap, ilgili SHA için sahip onayını yorumla verdi. Resmî GitHub review listesi boştu. [Kaynak rapor](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/a281caec295487b78371bac1e106cb378fa64bba/report.md) · [Onay](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/44#issuecomment-6587201791) · [Governance CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41515819414) · [Dependency gate](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41515952397)
- **F00-V0.** Java envanter/sipariş pilotu, V0 ve sabit JUnit testleri kabul edildi. Tarihsel uygulayıcı ve atanan kişi Cafer’di. GitHub, PR yazarını ve üç kaynak commit’in hesap bağlantısını `caferkilinc` olarak gösterdi. Cafer yalnızca ADR 0006’daki revizyon için yetki devri yorumunu verdi. Burkay adına bir GitHub onayı veya resmî bir review gözlenmedi. [Kaynak rapor](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/d923134da4f9f5a2ab55a5f51fbf9415ff717262/report.md) · [Devredilmiş onay](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45#issuecomment-6617013699) · [PR kapısı](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41688380131/attempts/3) · [Merge pilot CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41731529368) · [Merge governance CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41731529429)

İki issue da GitHub’da tamamlanmış olarak kapalıydı. Merge commit’leri kaynak `main`in atalarıydı ve bağlı CI koşuları başarılı sonuç verdi. Bu iki kabul kaydı **F00 faz kilidi oluşturmaz**.

## Anlık görüntüde aktif geliştirme

`F02-CONTRACT` [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) açıktı. Doğrulanan görev kaydındaki durum `ASSIGNED`, uygulama durumu `NOT_STARTED`, aktif geliştirici `Yaman-A-E` ve rotasyon indeksi 2 idi. `handoff_confirmed=false` bu göreve aitti. Sonraki kişi İsmail Çevik’tir ve geçiş kabul koşuluna bağlıdır. #11’in tek doğrulanmış doğal önkoşulu #8’di. #9 önceki devir kanıtıdır. [Kayıtlı devir ve görev sınırı](../handoffs/F00-V0-to-F02-CONTRACT.md)

## Yönetişim geçmişi

| PR | Doğrulanan birleşme (Europe/Istanbul) | Tarihsel etkisi |
|---|---|---|
| [#38](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38) | 27 Ekim · `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c` | Cafer’in temel yönetişim PR’ı Burkay tarafından birleştirildi. Genesis öncesi hazırlık, rotasyon tüketmedi. |
| [#39](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/39) | 27 Ekim · `5c297836b9ec70112e7b662eac05ec966543a134` | Yedi dil P0 kapsamı, v2 SRS, plan ve güvenli iş akışı entegre edildi. Ayrı bir ürün görevi kabulü yoktu. |
| [#44](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/44) | 2 Kasım · `ac321cb43fdea3f6b64bb1631de8daca8cf1d229` | F00-PLAN araştırma temeli birleştirildi. Ardından [kabul kaydı](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/0d05fcb2b4debec124bc874910bc9ec811094329) Burkay’dan Cafer’e tek geçişi kaydetti. |
| [#46](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/46) | 4 Kasım · `2584fbd97c6bd5e28e09be4199d895db5ff6791c` | ADR 0006 ile #45’in belirli SHA’sına sınırlı yetki devri entegre edildi. Genel yetki veya rotasyon adımı oluşturmadı. |
| [#45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45) | 4 Kasım · `fdd573286834fe15c1ac1c0d51db4ed9b0015db7` | Java V0 pilotu birleştirildi. Kabul ve rotasyon, sonraki #47 idari kaydıyla doğrulandı. |
| [#47](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/47) | 4 Kasım · `3d43a94fbf494360dfec1e7fb852cc99100d51eb` | #9 kabulü ve `F00-V0:d923134da4f9f5a2ab55a5f51fbf9415ff717262` anahtarı kaydedildi. Cafer → Alperen geçişi 1 → 2, bir kez gerçekleşti. |

## Açık riskler ve kanıt sınırları

- **#43**, anlık görüntüde açık UML görselleştirme PR’ıydı. Yönetişim, belge ve güvenlik işleri başarılıydı. `dependency-gate` ve `merge-readiness` başarısızdı. Görseller, onaylanmış mimarinin yerine geçmez. [PR #43](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/43) · [Kapı koşusu](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/40593283213)
- **#48**, anlık görüntüde açık pilot bütünlüğü ve durum düzeltmesi PR’ıydı. PR head’indeki dokuz dondurulmuş dosya #47’nin kabul anındaki Git ağacıyla eşleşti. #48’de `pilot-checks` başarılıydı, `dependency-gate` ve `merge-readiness` başarısızdı. PR head’indeki sonuç kaynak `main`e uygulanamaz. [PR #48](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/48) · [Pilot koşusu](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41771278729) · [Kapı koşusu](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41771613366)
- **Dondurulmuş pilot.** Kaynak `main`deki dokuz dosya #47 ağacından farklıydı. `verify_integrity.py`, `v0-source.json` özet uyuşmazlığı verdi. Tarihsel F00-V0 kabulü korunur. F00 kapanışı veya kilidi için güncel bütünlük sorunu ayrı kanıtla çözülmelidir.
- **Ürün ve araştırma.** Bir pilot ve iki kabul, tam ürün veya yedi dil doğrulaması sağlamaz. Deney veri seti `NOT_FROZEN`, çalışma `NOT_RUN`, sürüm `NOT_READY` olarak kaydedilmiştir. Falcon-Mamba model revizyonu, uyumlu GPU/runtime, bellek ve gecikme ile sağlayıcı erişimi/bütçesi için gerçek ölçüm gerekir. [Proje durumu](../PROJECT_STATUS.md) · [Araştırma temeli](../DECISIONS/0005-f00-research-baseline.md)
- **Zorunlu CI.** Göreve bağlı test ve bağımlılık kanıtı güncel SHA’ya bağlanır. Örneğin #11 için `governance-tests`, `documentation-checks`, `security-checks` ve `contract-checks` gerekir. Anlık görüntüde GitHub dal API’si `main` için `protected: false` döndürdü. Bir işin CI’da var olması, GitHub’da zorunlu koruma olarak etkin olduğu anlamına gelmez. [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) · [Dal durumu API’si](https://api.github.com/repos/caferkilinc/refactoring-ai-generated-code/branches/main)

## Mimari karar kayıtları

Kurs kapsamı ve kanıt modeli [ADR 0001](../DECISIONS/0001-scope-and-governance.md), sıralı sahiplik [ADR 0002](../DECISIONS/0002-project-genesis-v2-transition.md), yedi dil ve bağımlılık genişlemesi [ADR 0003](../DECISIONS/0003-mandatory-seven-language-delivery.md) ile kayıtlıdır. Tarihsel sahip onayı [ADR 0004](../DECISIONS/0004-sole-owner-approval.md), araştırma protokolü [ADR 0005](../DECISIONS/0005-f00-research-baseline.md), #45’in dar yetki devri [ADR 0006](../DECISIONS/0006-pr45-revision-bound-delegation.md) kapsamındadır.

## Codex-native geçişi

| Geçiş fazı | Adı | Anlık görüntü |
|---|---|---|
| `MIG-01` | Governance Migration | `REVIEW`. Dal ve commit yayımlanmış. Bu dala ait PR ve head kontrol koşusu gözlenmedi. Entegrasyon, kabul ve kilit kanıtı yok. |
| `MIG-02` | Skills & Context Engineering | `PLANNED` |
| `MIG-03` | Task Execution & Verification | `PLANNED` |
| `MIG-04` | Safe Publication & Acceptance | `PLANNED` |
| `MIG-05` | Next-Step Prompt Generation & E2E | `PLANNED` |

Geçiş fazları ürün fazlarından ve geliştirici rotasyonundan ayrıdır. MIG-01, kimliğe ve SHA’ya bağlı geliştirici onayı, korumalı yollar ve salt okunur devir önerisi kodunu içerir. [Yayımlanan MIG-01 commit’i](https://github.com/caferkilinc/refactoring-ai-generated-code/commit/3421531b530abde42e7d04bfcddcbc87b3993b9c) · [v3 tasarımı ve etkinleştirme koşulları](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md)

## Durumu yorumlama ve bağlamı geri yükleme

1. Kanonik uzak depoyu ve canlı `main` SHA’sını doğrula. Yeni karar vermeden önce geçerli politika, görev kaydı, kabul kaydı, SRS/mimari ve ilgili Issue, PR, CI kanıtını bu kaynağa göre oku.
2. Görev kabulünü kayıtlı issue/PR, tam kaynak SHA, CI SHA, birleştirme ve bağımsız kabul kanıtından doğrula. Atanan kişi, uygulayıcı, PR yazarı, commit yazarları, inceleyen ve insan onaylayan için ayrı kaynak kullan. Kanıt yoksa alanı bilinmiyor bırak.
3. Faz kilidi için görev kabullerine ek olarak tüm zorunlu faz ölçütlerini, GitHub kanıtını ve yetkili kilit kaydını doğrula. [Faz kilidi ve geçmiş eki](../governance/migrations/PHASE_1_HISTORY_AND_LOCKING_ADDENDUM.md) · [Tarihsel faz tohumu](../governance/migrations/CODEX_NATIVE_PHASE_LEDGER_SEED.json)
4. Düzeltmeyi eski olayı silmeden yeni yetkili kayıtla ilişkilendir. Yeni geliştirici, mevcut tek görevini ve önkoşullarını güncel kayıttan belirler, ilgili handoff’u okur ve yürütme yetkisini ayrıca doğrular.

## Tarihsel sınırlamalar

Bu belge, erişilebilir Git/GitHub kaynaklarına dayanan tarihsel bir yeniden oluşturmadır. Orkestrasyon sohbetlerinin tam dökümü, özel kaynak PDF’leri, çevrimdışı yetki kayıtlarının tamamı ve pilot üretim modelinin kesin sunum parametreleri erişilebilir kanıtla doğrulanmadı. Bilinmeyen katkılar, zamanlar ve izinler geriye dönük olarak uydurulmaz. Açık PR ve görev durumları yeni çalışmada yeniden sorgulanır.
