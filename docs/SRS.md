# Yazılım Gereksinimleri Şartnamesi (SRS)
# Yapay Zekâ Tarafından Üretilen Kodun Güvenli Refactoring ile İyileştirilmesi

**Kimlik:** RAGC-SRS-001  
**Sürüm:** 0.2.0  
**Tarih:** 2026-10-26  
**Durum:** İNCELEME TASLAĞI — proje sahibinin kapsam onayı mevcuttur; bu derlemenin ayrı son kabulü henüz kaydedilmemiştir.  
**Sistem:** AI-Generated Code Refactoring and Quality Evaluation / Engineering Design II  
**Hedef teslim:** 2027-01-01; kesin saat henüz doğrulanmadı.  
**Teknik otorite:** 01_Master_Sistem_Mimarisi.pdf (v2.0) → 02_Adim_Adim_Gelistirme_Rehberi.pdf (v2.0) → 04_Modular_Architecture_Visual_Presentation.pdf ve PPTX ile 2026-10-20 mimari görseli.  
**Eski ve ikincil kaynaklar:** 01_System_Operation_and_Architecture.pdf (v1.0) ve 03_Technical_System_Presentation_Revised.pdf; yalnızca güncel v2.0 ile çelişmeyen ayrıntılarda kullanılabilir.  
**Uygulama takibi:** GitHub F00–F15 planı, 31 mevcut teknik görev ve onların bağımlılıkları.  
**Yürütme otoritesi:** Project Genesis v2.0; ürün gereksinimleri yerine geçirilmez.

> Bu SRS planlanan sistemi tanımlar. Buradaki hiçbir gereksinim tamamlanmış/ölçülmüş/deploy edilmiş kabul edilmez. Uygulama durumu kaynak kod, çalışan testler ve kabul edilen Git kanıtlarıyla ayrıca belirlenir.


## 1. Amaç, kullanıcılar ve ürün sınırı

Geliştirici, kendisinin işleme yetkisi bulunan AI-generated veya diğer kaynak kodunu ZIP, klasör veya snippet olarak yükler. Sistem yapısal kod kalitesini ve deterministik güvenlik kanıtlarını tarar; başlangıç davranış testlerini izole ortamda saptar; kullanıcıya dosya/satır düzeyinde bulguları gösterir. Kullanıcı yalnızca seçtiği uygun kod kalitesi bulgularında refactoring başlatır (Onay 1); LLM değişiklikleri kontrollü patch olarak üretir; sistem ayrı çalışma kopyalarında test eder; kullanıcı gerçekten doğrulanmış patch'leri inceleyip seçer (Onay 2); sistem taze V0 üzerinden birleşimi tekrar doğrular ve final ZIP, HTML/PDF raporları, sayısal karşılaştırmalar ve geçmiş sunar.

**Aktörler:** Kod sahibi/geliştirici; uygulama operatörü; akademik denetçi; deterministik analiz ve security işçileri; izole build/test worker; izin verilen bulut refactoring sağlayıcısı; isteğe bağlı yerel Falcon-Mamba inceleme servisi. Codex geliştirici asistanıdır, ürünün otonom onay otoritesi değildir.

**Dahil:** Gerçek dosya değişikliği, iki kullanıcı onayı, çok dilli yetenek bildirimi, kaynak kanıtı, güvenlik taraması, frozen testler, sınırlı paralellik, tekrar doğrulama, karşılaştırma/rapor/indirme ve akademik ölçüm.

**Hariç:** Kullanıcının haberi olmadan bütün projeyi yeniden yazmak; güvenlik açıklarını otomatik ve garantili kapatmak; özgün programın tüm davranışını matematiksel kanıtlamak; testleri değiştirilerek sahte yeşil sonuç üretmek; isteğe bağlı olmayan ücretli sağlayıcı çağrıları; doğrulanmamış yerel model güvenlik kararını tek başına uygulamak.

## 2. Onaylanmış hedef mimari ve bileşen sözleşmeleri

| Bileşen | Hedef teknoloji ve sorumluluk | Kabul ilkesi |
|---|---|---|
| Web uygulaması | React, TypeScript, Tailwind, Monaco Editor, ECharts | Upload/Issue Explorer, iki kullanıcı onayı, diff, metrik ve geçmiş |
| Core Backend | Python, FastAPI, Pydantic | İşlerin orkestrasyonu, dil router, policy, şema, API ve durum makinesi |
| Queue/Workers | Redis + RQ | HTTP'yi bloke etmeyen, restart ve idempotency kontrollü işler |
| Metadata & artifact | SQLite, SQLAlchemy/Alembic; içerik adresli yerel storage, opsiyonel S3 | Değişmez V0, sürümler, bulgular, denemeler, testler, log/rapor/ZIP |
| CIR / Core | Finding Normalizer, Evidence Registry, Correlator, Eligibility, Metric Normalizer | Kanıt ve belirsizlik korunur; quality, security ve baseline farklı sınıflar |
| Java adapter | JavaParser Symbol Solver, Java 21/Maven, PMD, CPD, JUnit 5, JaCoCo | P0 çalışan pilot ve gerçek araç çıktısı; SonarQube ek servis opsiyonel |
| Python adapter | Python ast/LibCST, Ruff/Pylint, pytest, coverage.py | P1; belirsiz dinamik referanslar açık gösterilir |
| JS/TS adapter | TypeScript Compiler API/ts-morph, ESLint, tsc, Vitest/Jest, coverage | P1; modül ve lockfile sınırlarına riayet |
| İleri adapter | C#, Go, C++: Roslyn, Go araçları, Clang | Gelecek kapsam; implement edilmiş gibi sunulmaz |
| Security | Gitleaks, Semgrep, OSV-Scanner | Gerçek tarama/evidence; unavailable temiz sayılmaz |
| Yerel güvenlik AI | Falcon-Mamba 7B hedefi; runtime, varyant, Q8 ve GPU henüz doğrulanacak | Yardımcı güvenlik açıklaması; opsiyonel ve bozulmaya dayanıklı |
| Refactoring | Bounded Context Builder, Conflict Detector, DeepSeek/GLM/Qwen provider adaptörleri | Gerçek, izinli unified diff; sağlayıcı ve maliyet onayına bağlı |
| Sandbox Validation | Izole container/VM worker; dil bazlı build/tests/scans | Güvenilmeyen kod ana FastAPI sürecinde/hostta çalışmaz |
| Reporting | Before/After engine, HTML/PDF, audit, history, ZIP | Sayısal veriler ölçümden; AI anlatımı kanıta bağlı |

**P0 / P1 yorumu:** P0, ders için gerçek Java yüklemeden son ZIP+HTML/PDF'ye uzanan, deterministik güvenlik ve kabul zinciridir. P1, diğer dillerin olgun safe-patch desteği, yerel Falcon-Mamba ve ilave rapor zenginliğidir; v2.0 hedef mimariden çıkarılmaz, ancak doğrulanmadan zorunlu çekirdeği bloke etmez. Çalışmayan bileşenler açıkça Unsupported/Unavailable gösterilir.

## 3. Zorunlu uçtan uca ürün iş akışı

1. **Girdi ve izin:** ZIP/klasör/snippet kabulü; dosya manifesti, dil algılama, gizlilik/dinamik çalışma/bulut izni.
2. **Dil yönlendirme:** Dosya ve bileşen bazında adapter seçimi, yetenek bildirimleri, bilinmeyen dil/bağımlılık uyarısı.
3. **Başlangıç paralel analiz:** (A) statik kalite, (B) Gitleaks/Semgrep/OSV ve opsiyonel yerel yorum, (C) izolasyonda başlangıç build/test/coverage. Dinamik iş güvenli sandbox olmadan başlamaz.
4. **Issue Explorer ve Onay Kapısı 1:** Kaynak kod/satır kanıtlı bulgular; yalnız uygun QUALITY_REFACTOR adayları; değişmez issue-selection snapshot.
5. **Dependency-Aware Context Builder:** Hedef sembol, çağıran/çağrılanlar, imzalar, testler, yan etkiler, izinli bağlam; read/write set ve conservative conflict DAG.
6. **Patch Engine:** En çok üç kanıtlanmış bağımsız iş, tek aday dizisi/iş, sağlayıcı API, kısıtlı JSON+unified diff; her iş bağımsız workspace.
7. **Candidate Validation:** Syntax/type/build, frozen regresyon, kalite/security yeniden tarama; davranış ve kalite ayrı; en fazla ilk deneme + iki düzeltme.
8. **Onay Kapısı 2 ve birleşik final:** Monaco Diff ile tüm denemeler; yalnız normal onaya uygun adaylar. Taze V0 kopyasında seçilen patch'ler deterministik sırayla birleşir; tam frozen suite ve kurallar yeniden çalışır.
9. **Sonuç ve geçmiş:** Başarılı combined validation sonunda değişmez final sürümü, indirilebilir ZIP ve HTML/PDF, before/after, audit ve History. Başarısız/UNVERIFIED çalışmalar yalnız açık uyarılı taslak olarak kalır.

**Değişmez kurallar:** V0 SHA-256 ve sabit testler refactoring boyunca aynı kalır; onaylar birbirinden bağımsızdır; güvenlik bulgusu otomatik kalite refactoring konusu olamaz; modellerin kendi başarı iddiası kontrol sonucu değildir; sonuçlar ölçüm kanıtı olmadan yeşil sayılmaz.

## 4. Durum makinesi, sonuç sözlüğü ve veri asgari sözleşmesi

**Normal iş sırası:** UPLOADED → BASELINE_CREATED → LANGUAGE_ROUTED → ANALYZING → FINDINGS_READY → AWAITING_ISSUE_SELECTION → REFACTORING → VALIDATING_CANDIDATES → AWAITING_PATCH_APPROVAL → COMBINED_VALIDATION → FINALIZED → REPORT_READY. İlgili hatalı/terminal durumlar: BLOCKED_INPUT, BASELINE_FAILURE, UNVERIFIED, PATCH_FAILED, MERGE_CONFLICT, USER_CANCELLED. Geçersiz geçiş sunucu tarafında reddedilir ve kayıt altına alınır.

**behavior_status:** PASSED, FAILED, UNVERIFIED. **quality_outcome:** IMPROVED, UNCHANGED, WORSE, NOT_COMPARABLE. PASSED + UNCHANGED mümkündür; UNVERIFIED kalite iyileşmedi demek değildir. Bir güvenlik tarayıcısının çalışmaması CLEAN değil INCOMPLETE/UNAVAILABLE'dır. Yetersiz güvenlik kanıtı ya da yeni kritik bulgu, tanımlı onay politikasına göre finali engeller.

**Asgari mantıksal varlıklar (fiziksel tablo emri değil):** Project, ProjectVersion, FileManifest, Artifact; AnalysisRun, ToolExecution, Finding, Evidence, Metric; SourceLocation, Symbol, DependencyEdge, ProjectComponent, Capability; BaselineTestSuite, TestRun, CoverageRun; IssueSelection, ContextPackage, RefactorJob, Attempt, PatchCandidate, ValidationResult; PatchApproval, CombinedValidation, FinalVersion/Export; AuditEvent, Report. Her kayıtta ilgili actor, project/version, timestamp UTC, hash ve kaynak aracın sürüm/kuralları saklanır.

**İdempotency:** Etkili POST operasyonları tekrar gönderildiğinde ikinci job/approval yaratılmaz. Yeniden başlayan worker, kalıcı state/attempt üzerinden devam eder. Şema ve hata nedenleri versiyonlanır. Aşağıdaki endpointler rehberin tasarlanan örnekleridir, yürürlükte API implementasyonu iddiası değildir: POST /api/projects; POST /api/projects/{id}/versions; POST /api/versions/{id}/analyze; GET /api/analyses/{id}/findings; POST /api/analyses/{id}/issue-selections; POST /api/refactoring-jobs; GET /api/refactoring-jobs/{id}; GET /api/patches/{id}/diff; POST /api/refactoring-jobs/{id}/approvals; POST /api/refactoring-jobs/{id}/finalize; GET /api/comparisons/{id}; POST /api/versions/{id}/reports; GET /api/projects/{id}/history; GET /api/jobs/{id}/events; GET /api/artifacts/{id}/download.

## 5. Fonksiyonel gereksinimler

Gereksinim kabulü için her satır gerçek davranış testi, kanıtlı kaynak çıktı veya gerekli durumlarda kullanıcı onayı ile doğrulanacaktır. Issue numaraları var olan GitHub kayıtlarıdır.

| ID | Öncelik | Zorunlu davranış / kabul ölçütü | Plan kaynağı |
|---|---|---|---|
| FR-001 | P0 | ZIP, klasör ve snippet girişini destekle; manifest, dosya hash'i, dil ve excluded-path açıklamasını üret. | F03-INPUT/#13 |
| FR-002 | P0 | Arşivde traversal, symlink, Unicode/path çakışması, aşırı sıkıştırma, boyut ve dosya sayısı aşımlarını reddet. | #13 |
| FR-003 | P0 | Yüklemenin byte/hash V0 kopyasını değişmez sakla; tüm analiz/patch/final işlemlerini ayrı V0 klonlarında yap. | #9,#13,#29 |
| FR-004 | P0 | Terms, saklama, bulut kod gönderimi ve dinamik çalıştırma izinlerini ayrı sürüm/zaman/actor ile sakla. | #13 |
| FR-005 | P0 | Sahiplik/yetki denetimini tüm proje, history ve artifact download işlemlerinde uygula. | #13,#31 |
| FR-006 | P0 | Versiyon, job, approval, attempt ve durum geçişini kalıcı sakla; yasa dışı geçiş, replay ve duplicate POST'u reddet. | #12 |
| FR-007 | P0 | CIR şemalarını Finding, Evidence, SourceLocation, Symbol, DependencyEdge, Metric, TestResult, PatchCandidate ve ValidationResult için sürümle. | #11 |
| FR-008 | P0 | Kullanıcı dili seçse de dosya ve bileşenleri ayrı tespit et; unknown dosyayı yanlış adapter'a sessizce yönlendirme. | #14 |
| FR-009 | P0 | Java 21/Maven AI-generated çalışan V0 pilotunu özgün prompt/model/attempt ve sabit test/hash ile kayıt altına al. | #9 |
| FR-010 | P0 | JavaParser Symbol Solver ile Java symbol, overload, source range ve belirsiz referansları kanıta dayalı çıkar. | #14 |
| FR-011 | P0 | LanguageAdapter parse/quality/dependency/test/coverage/safe_patch desteklerini ayrı capability ve confidence ile bildir. | #14 |
| FR-012 | P0 | Gerçek PMD/CPD kalite taramasında en az dört uygun kategoriye dair rule, tool version, file/line kanıtını CIR'a dönüştür. | #15 |
| FR-013 | P0 | SonarQube olmadan PMD/CPD P0 uçtan uca çalışabilsin; varsa SonarQube ayrı servis/veritabanı kullansın. | #15 |
| FR-014 | P0 | Kaynak analizini normalize ve korele et; farklı tools kaynak kanıtlarını kaybetmeden tekil finding ilişkisi kur. | #15 |
| FR-015 | P0 | Gerçek Gitleaks, Semgrep, OSV taramalarını uygun kapsamda işlet; sonuçlar ve kapsanmayan alanlar açık. | #18 |
| FR-016 | P0 | Bulgu/prompts/UI/log/PDF içinde secret maskele; LLM suspected bulgularını doğrulanmış security finding olarak sunma. | #18,#20 |
| FR-017 | P0 | Security findings yalnız SECURITY_REVIEW sınıfında tutulur; P0 quality refactoring seçiminde normal onay verilemez. | #18,#21 |
| FR-018 | P0 | Güvenilmeyen build/test süreçlerini izole non-root worker'da, default kapalı ağ ve kaynak limitleriyle çalıştır. | #16 |
| FR-019 | P0 | Sandbox bilinmeyen/güvensiz ise dinamik yürütmeyi kapat; host secrets, Docker socket ve host path erişimini engelle. | #16 |
| FR-020 | P0 | Mevcut Java JUnit/JaCoCo suite ve coverage'ı V0'da çalıştır; stable test-case ID, suite hash, ortam izi sakla. | #17 |
| FR-021 | P0 | Test eksikse V0 kopyasında gerçek gözlenen davranışla characterization tests üretmeyi dene; V0'da geçenleri dondur. | #17 |
| FR-022 | P0 | Baseline bozuk, environment eksik, test yok ve yeni regresyonu farklı neden/status ile raporla; build-only PASSED verme. | #17 |
| FR-023 | P0 | Quality/Complexity/Duplication/Security/Baseline filtreleri ve gerçek satır vurguları olan Monaco Issue Explorer sun. | #21 |
| FR-024 | P0 | Çift taraflı duplication source location göster; unknown/error/disabled UI durumlarını ve fixture modunu etiketle. | #21 |
| FR-025 | P0 | Onay 1 seçimini analysis_id, immutable V0 ve seçilmiş eligible issue fingerprint/snapshot ile kaydet. | #22 |
| FR-026 | P0 | Server, unauthorized issue ve broken-baseline refactoring bypass isteklerini reddeder; tekrar gönderim idempotenttir. | #22 |
| FR-027 | P0 | Target symbol, callers/callees, tests, models, side effects ve public API'den sınırlı, masked ContextPackage üret. | #23 |
| FR-028 | P0 | Context budget aşıldıysa önemli bağımlılığı sessiz atma; ek bağlam iste veya işi güvenle durdur. | #23 |
| FR-029 | P0 | Read/write-set ve bilinmeyen ortak contract durumuyla conservative conflict DAG oluştur; çakışan işleri seri yürüt. | #24 |
| FR-030 | P0 | En fazla üç doğrulanmış bağımsız refactoring işi paralel; her job izole workspace ve immutable input hash kullanır. | #24 |
| FR-031 | P0 | İzinli gerçek provider'dan schema-valid unified diff ve açıklama al; değişiklik dosyaları ve kapsamı whitelist ile sınırla. | #25 |
| FR-032 | P0 | Ücretsiz/ücretli model sınırları, token ve egress izni sağlanmadan hassas kod veya ücretli çağrı gönderme. | #25 |
| FR-033 | P0 | Patch testleri, kural seti, korumalı dosyaları değiştiremez; invalid schema/diff/out-of-scope değişiklikler reddedilir. | #25 |
| FR-034 | P0 | Tekil patch için syntax/build, frozen test, hedef finding, coverage ve güvenlik yeniden değerlendirmesi çalıştır. | #26 |
| FR-035 | P0 | behavior_status ile quality_outcome'u ayrı hesapla ve sakla; yeni riskler/iyileşmeyen hedef açıkça görünür. | #26 |
| FR-036 | P0 | En fazla 1 ilk deneme + 2 correction attempt; transport retry ayrı; bütçe worker restart sonrası da korunur. | #27 |
| FR-037 | P0 | Monaco Diff ve deneme günlüğü içinde tüm patch hunks, model, teknik, status ve kanıtları incelet. | #28 |
| FR-038 | P0 | Onay 2 yalnız doğrulaması izinli patch ID'leriyle mümkündür; failed/unverified normal finale seçilemez. | #28 |
| FR-039 | P0 | Onaylanmış patch'leri taze V0 klonuna deterministik uygula; collision/combined regression ve full rescans yap. | #29 |
| FR-040 | P0 | Bütün zorunlu birleşik doğrulama kapıları geçmeden VALIDATED final ZIP/etiket yayınlama. | #29 |
| FR-041 | P0 | Final ZIP/HTML/PDF download, source-version ilişkisi ve History'den yeniden erişim sun; sahibi dışında indirme yok. | #29,#30,#31 |
| FR-042 | P0 | Aynı ruleset/toolversion/scope ile önce-sonra finding/complexity/duplication/coverage hesapla; karşılaştırılamazı belirt. | #30 |
| FR-043 | P0 | Zero denominator=N/A, percent ile yüzde puanı ayrı, failed/new findings saklı ve tüm numerikler kanıta bağlı. | #30 |
| FR-044 | P0 | HTML ve PDF minimum kanıt raporlarında aynı run/ölçüm kimlikleri kullan; sırları maskeler; AI anlatımı ölçüm icat edemez. | #30,#31 |
| FR-045 | P0 | Gerçek Java upload → analysis → onay1 → real patch → individual validation → onay2 → combined validation → ZIP E2E çalışsın. | #35 |
| FR-046 | P0 | Bozuk baseline, testsiz kod, provider timeout, conflict, secret masking, combination regression E2E negatif durumlarını göster. | #35 |
| FR-047 | P0 | Akademik deney en az 12 sabit refactoring görevi ve tüm başarısız denemeleri ölçüm paydasına dahil etsin. | #8,#36 |
| FR-048 | P0 | Sequential/parallel koşullarını aynı context/test/rule ayarlarında üçer tekrar karşılaştır; süre/tokencost gerçek ölçülsün. | #36 |
| FR-049 | P0 | En az %50 finding azaltma hedef olarak ölçülsün, başarı ya da eşdeğerlik önceden iddia edilmesin. | #36 |
| FR-050 | P0 | Final reproducibility bundle V0/V1 hash, generation prompt, gerçek testler, uyumlu build/demo, sınırlamalar içersin. | #37 |
| FR-051 | P1 | Python ast/LibCST, Ruff/Pylint, pytest/coverage ile gerçek adapter capability sağlar; Java regression korunur. | #32 |
| FR-052 | P1 | JS/TS TS Compiler API, ESLint, tsc, Jest/Vitest ve coverage ile gerçek adapter capability sağlar. | #33 |
| FR-053 | P1 | Karma projede component bazlı ölçüm, cross-service belirsizliği ve language-specific test semantiğini koru. | #34 |
| FR-054 | P1 | Falcon-Mamba 7B'nin tam repo/variant/quantization/GPU/runtime/VRAM/latency uygunluğunu pilotla; disabled fallback sun. | #19 |
| FR-055 | P1 | Yerel AI yalnız maskelenmiş, evidence-referenced, UNCONFIRMED inceleme döndürür; arızası deterministik SAST'ı bozmaz. | #20 |
| FR-056 | P1 | Falcon-Mamba için bağımsız etiketli örneklerle precision/recall, FP/FN paydalarını raporla. | #20 |
| FR-057 | P1 | Opsiyonel ayrıntılı AI anlatımı ve gelişmiş PDF raporlarında backend sayıları ve HTML parity korunur. | #31 |

## 6. Fonksiyonel olmayan gereksinimler

| ID | Öncelik | Kısıt ve doğrulama | Kaynak |
|---|---|---|---|
| NFR-01 | P0 | İzolasyon: non-root, network default deny, CPU/RAM/time/process limit, file/secret sınırı; saldırgan fixture testleri. | #13,#16 |
| NFR-02 | P0 | Bütün orijinal byte'lar ve frozen testlerin SHA-256 bütünlüğü her relevant aşamada tekrar doğrulanır. | #9,#13,#29 |
| NFR-03 | P0 | Project owner/actor, ayrı izinler, dış API redaction ve saklama/silme politikası denetlenir. | #13,#18,#31 |
| NFR-04 | P0 | Tool/ruleset/config/coverage-scope/test-suite/env fingerprints before/after karşılaştırmasını tekrarlanabilir kılar. | #15,#17,#30 |
| NFR-05 | P0 | Hiçbir test NOT_RUN sonucunu PASS yapma; provider/model sahte success ya da eksik scan'i temiz sayma. | #26,#35 |
| NFR-06 | P0 | Asenkron işler worker restart/cancel ve idempotency durumlarından veri kaybı/double write olmadan çıkar. | #12,#24 |
| NFR-07 | P0 | Frontend ve backend API şemaları versiyonlu; durum ve capability yanlış temsil edilemez. | #11,#21 |
| NFR-08 | P0 | Temiz checkout ile OS/tool support ve backend/frontend/queue/DB için gerçekten çalışan build/test talimatı. | #10 |
| NFR-09 | P0 | Gereksiz framework, class hierarchy, database/infra ve test enflasyonu olmadan minimum yeterli karmaşıklık. | Genesis v2 |
| NFR-10 | P0 | Metriklerin unit ve formülleri açık; farklı Sonar ve CPD tanımları birbirine karıştırılmaz. | #15,#30 |
| NFR-11 | P0 | API anahtarları browser'a veya depoya giremez; source comments prompt talimatı olarak yetki yükseltemez. | #18,#25 |
| NFR-12 | P0 | Run/attempt/approval/final ve UTC audit/History kalıcılığı; logda ham kullanıcı kodu ve secrets bulunmaz. | #12,#30 |
| NFR-13 | P0 | Model, donanım, benchmark ve teslim success iddiaları gerçek ölçüm ve koşullarla sınırlandırılır. | #19,#36 |
| NFR-14 | P1 | Dil adapter'ları capability flag, support güveni ve per-language coverage ile P0 Java'yı bozmaz. | #32–#34 |
| NFR-15 | P0 | Internet-facing deployment, ayrıca doğrulanmış threat model, izolasyon ve konfigürasyon/release kararına bağlıdır. | mimari v2 §16; rehber faz15 |

## 7. Kabul senaryoları ve çıkış kapıları

| Senaryo | Ölçülebilir beklenen sonuç |
|---|---|
| Tehlikeli ZIP, symlink, Unicode ve arşiv bomb | Reddedilir; hiçbir dosya çalışma alanı dışına çıkmaz; V0 korunur. |
| Testli Java/Maven gerçek pilot | Maven/JUnit/JaCoCo, JavaParser, PMD/CPD gerçek çıktı üretir; fixture değil gerçek analiz delili. |
| Gitleaks / Semgrep / OSV arızası | Secret maskelenir; bulunamayan advisory/engine INCOMPLETE, temiz değil. |
| Güvensiz worker / uzun döngü | Dinamik iş fail-closed; CPU/time ve ağ/host path kontrolleri. |
| Onay 1 bypass | Security veya invalid baseline ile refactoring başlatılamaz; immutable snapshot tutarlı. |
| Çakışan veya bilinmeyen ilişkiler | Paralellik reddedilir; üç bağımsız iş için max_parallel=3 uygulanabilir. |
| Patch format ve yazma sınırı ihlali | Scope guard reddeder; korumalı test/ruleset/V0 değişmez. |
| Başarısız patch ve iki tekrar | Deneme 0,1,2 kanıtları saklanır; dördüncü otomatik düzeltme yok. |
| Testsiz/baseline failed | UNVERIFIED/Baseline Failure gösterilir; normal final validasyonu yapılmaz. |
| İki tekil başarılı, birleşince başarısız patch | Combined validation FAILED; Validated ZIP çıkarılmaz. |
| Normal iki onaylı gerçek patch | Sadece onaylanan kod finalde, full suite ve static/security rerun geçer. |
| Before/After ve PDF/HTML/ZIP/History | Aynı run+unit+scope, zero denominator N/A, indirme ve tekrar erişim, secret redaction. |
| 12 görevli değerlendirme | Başarısızlıklar dahil denominators; üç tekrarlı karşılaştırma; sonuçlar ölçülmeden ilan edilmez. |

**Çıkış sınıfları:** IMPLEMENTED_UNVERIFIED, VERIFIED_COMPLETE (gereksinim kanıtı var), BLOCKED; release kararı ayrıca READY_FOR_RELEASE / READY_WITH_APPROVED_LIMITATIONS / NOT_READY / REVIEW_REQUIRED olarak verilir. Passing unit test ürünün tamamının üretim hazır olduğunu göstermez.

## 8. Kaynak-takip matrisi ve çalışma paketleri

Önceki task-plan.json içindeki **31 teknik görev (GitHub #1 ve #8–#37), altı araştırma paketi ve 54 native prerequisite ilişkisi** korunur; bunlar silinmeyecek, sabit kişi atamalarından ayrıştırılacaktır.

| İlgili işler | Gereksinim bölümü |
|---|---|
| F00-PLAN #8, F00-V0 #9 | FR-009, FR-047–050 |
| F01-GOV #1, F01-ENV #10 | GOV-001–008, NFR-08 |
| F02-CONTRACT #11, F02-STATE #12 | FR-006–007, durum/veri sözleşmeleri |
| F03-INPUT #13 | FR-001–005 |
| F04-JAVA #14, F05-QUALITY #15 | FR-008–014 |
| F06-SANDBOX #16, F06-TESTS #17 | FR-018–022 |
| F07A-SCAN #18, F07B-PILOT #19, F07B-LOCAL #20 | FR-015–017, FR-054–056 |
| F08-UI #21, F08-INTEGRATE #22 | FR-023–026 |
| F09-CONTEXT #23, F09-SCHED #24 | FR-027–030 |
| F10-PATCH #25, F11-VALIDATE #26, F11-RETRY #27 | FR-031–036 |
| F12-REVIEW #28, F12-FINAL #29 | FR-037–040 |
| F13-BASIC #30, F13-ADV #31 | FR-041–044, FR-057 |
| F14-PY #32, F14-JSTS #33, F14-MIX #34 | FR-051–053 |
| F15-P0 #35, F15-EXPERIMENT #36, F15-HANDIN #37 | FR-045–050 |

**Düzeltme notu:** PDF/HTML çıktı v2.0 mimaride ürün hedefidir; P0 minimum HTML/PDF erişimi ve parity için izlenen #30/#31 görev tanımları, değişiklik gerekirse ayrı change request ile yeniden düzenlenmelidir. Mevcut P1 öncelik kaydı sessizce değiştirilmez. İlk refactoring araştırması için Java P0'ı öncelerken P1 adapter hedefleri silinmez.

## 9. Project Genesis ekip yönetişimi (ürün onaylarından ayrıdır)

- **GOV-001:** Yetkili beşli: Burkay (@cakarburkayy), Cafer (@caferkilinc), Alperen Enes Yaman (@Yaman-A-E), İsmail (@ismail-cevik), Uğur = Taha Uğur Toyran (@tahaugurtoyran).
- **GOV-002:** Tek aktif uygulama sahibi ve sabit tur: Burkay → Cafer → Alperen → İsmail → Uğur → Burkay. Onaylanmayan/başarısız görev devri artırmaz.
- **GOV-003:** 'main' proje sahibinin kabul ettiği ortak entegrasyon dalıdır. Numaralı PR dalları gerçek bağımsız inceleme için kalabilir; otomatik birleşme veya review atlama yoktur.
- **GOV-004:** Eski issue/plan içindeki primary/support/reviewer alanları *kalıcı uygulama yetkisi* sayılamaz; ekip rolü/uzmanlığı ayrı tutulur. Issue assignee'leri ve sabit görevlendirmeler, gate/CI/plan/audit/test uyumu sağlandıktan sonra kontrollü olarak kaldırılır. Issue'ları, tarihsel commits'i veya dependency edges'i silme.
- **GOV-005:** Devir: bir task → Codex kod/yakın test/diff/report → insan incelemesi → commit ve push → rapor ve gerçek SHA → orkestratör acceptance → tam bir rotation. Aynı task+SHA bir kere sayılır.
- **GOV-006:** Codex yalnızca geçerli iş kontratını uygulayabilir; sonraki görev, branch politikası, mimari veya production-release kararını tek başına değiştiremez.
- **GOV-007:** Varsa mevcut docs/DEVELOPMENT_ROADMAP.md, docs/PROJECT_STATUS.md, docs/DECISIONS/ ve .github/acceptance.json tekrar kullanılır; rakip state dosyaları oluşturulmaz.
- **GOV-008:** PR #38'in önce gerçek bağımsız incelemesi, mevcut revizyon kontrolleri ve insan merge kararı korunur. Yeni governance geçişi, bu bootstrap'ın onayını geçmiş gibi temsil edemez.

## 10. Kaynak uzlaştırması ve açık karar kayıtları

| Kod | Çelişki / belirsizlik | Güncel hüküm ve gerekli kanıt |
|---|---|---|
| DEC-001 | Eski architecture v1 ve eski presentation v1 | Yeni Master Mimari v2 + Adım Adım Rehber v2 öncelikli. Eski metin yalnız çelişmezse kullanılacak. |
| DEC-002 | Akademik 12 haftalık öneri ve GitHub son tarih | 2027-01-01 owner/GitHub deadline; kesin saat ve platform UNKNOWN. |
| DEC-003 | Görevlerin sabit primary/support/reviewer ataması | Project Genesis sıralı sahiplik esastır; CI gate ve 31 issue uyumlu migrasyon onaylanmadan assignee'ler birden kaldırılamaz. |
| DEC-004 | PR #38 eski dört/çok geliştiricili iş modeli için hazırlık | PR #38 inceleme/CI/merge korunur; henüz Genesis handoff kabulü değil. |
| DEC-005 | P0 Java vs mimari çok dil görüntüsü | Çok dilli mimari hedef; önce Java doğrulama zinciri. Python/JS/TS için P1 gerçek capability, C#/Go/C++ gelecek. |
| DEC-006 | Local Falcon-Mamba çekirdek görselleştirmesi | Deterministik SAST P0, yerel Falcon-Mamba 7B opsiyonel değerlendirme/servis; gerçek 16 GB GPU uyumluluğu ispatlanmadı. |
| DEC-007 | PDF raporu eski task-plan'da P1 ayrıntılı iş | Yeni Master+Rehber PDF/HTML'yi nihai kullanıcı çıktısı olarak bekliyor; minimum PDF için kapsam/öncelik revizyonu gözden geçirilmeli. |
| DEC-008 | Gerçek LLM patch sağlayıcısı ve kaynak aktarımı | Endpoint, model, kota, ücret ve kod aktarım izni doğrulanmalı; hiçbiri varsayılan veya fiilen kullanılabilir sayılmaz. |
| DEC-009 | Deployment, öğrenci demo ve halka açık hizmet | Yerel demo ile public servis ayrı security gereksinimlerine sahip; deployment kararı doğrulanmalı. |

## 11. Değişiklik ve kabul politikası

Bu sürüm **derleme taslağıdır**. Project owner'ın 2026-10-26 tarihinde yetkilendirdiği mimari/GitHub kaynak kararları uygulanmıştır; bu dosyanın nihai tekil SRS onayı henüz ayrı belirtilmemiştir. Ana SRS, API şeması, backend state ve mevcut task graph arasında uygulama esnasında bulunan bir çelişki bir change-request/ADR ile çözülür. Uygulama ilerleme yüzdeleri kanıtsız verilmez. Rehberin örnek API JSON'ları, sayısal değerleri ve test komutları gerçek sonuç olarak sunulamaz. Sürüm değişikliği SRS gereksinim kimliklerini yeniden kullanmaz.
