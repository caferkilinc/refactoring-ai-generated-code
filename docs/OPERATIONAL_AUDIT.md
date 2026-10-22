# İşleyiş ve güvenlik denetimi / Operational audit

23 Ekim 2026. Kapsam: PR #38, yönetim kodu/workflow’ları, 31 teknik görev, altı araştırma paketi, kaynak mimariyle eşleşme, 53 mevcut bağımlılık, özel Project görünümleri ve teslim takvimi. (Scope: governance implementation, live tasks/graph/board and delivery risks.)

Denetim başlangıç revizyonu `754e59656433f9be2055aca04a750003c97675b7`; main `7e068040c3a4fb1a2f32813a4c592dc974324f36`. İncelenen repository blob’ları yerel çalışma kopyasıyla karşılaştırıldı; SETUP_REPORT’taki yalnız ek satır sonu farkı güncel uzak içerik üzerinden korundu. Ürün kodu henüz main’de olmadığı için bu rapor bir ürün sızma testi veya tamamlanmış refactoring deneyi değildir. (The audit does not claim a product penetration test or completed experiment.)

**Sonuç:** Görev modeli tutarlı; ancak önceki 27 test, mevcut PR’nin bağımsız incelemesini, bütün karma modül kontrollerini ve eski-event yeniden çalıştırmasını yeterince kapsamıyordu. Bulguların yazılım düzeltmeleri PR #38’de hazırlanmıştır; merge/koruma hâlâ bağımsız inceleme ve canlı aktivasyon koşullarına bağlıdır. (The graph was consistent, but the original tests did not cover several merge and recovery boundaries.)

## Bulgular, etkiler ve çözümler

Önem dereceleri projenin işleyişine etkidir; doğrulanmış bir saldırı veya veri sızıntısı iddiası değildir. FIXED IN PR, düzeltmenin main’de aktif olduğu anlamına gelmez. (Severity describes operational impact; prepared fixes are not active protection.)

| ID / önem | Bulgu ve kanıt | İşleyişe etkisi | Çözüm ve durum |
|---|---|---|---|
| R01 / Kritik | main’de classic protection ve ruleset yok; PR #38 açık, inceleme listesi boş | Write sahibi doğrudan main’e yazabilir; CI yeşil görünse de zorunlu süreç henüz uygulanmaz | **BLOCKED:** Burkay’ın son SHA onayı → yetkili merge → canlı canary → denenmiş korumalar. Kullanıcı onayı kayıtlı; inceleme atlanmaz |
| R02 / Yüksek | Eski `evaluate()` güncel PR’de hiç review yokken başarılı dönüyordu; bağımsızlık yalnız daha sonra önkoşul kabulünde sınanıyordu | Support onayıyla birleşen iş bir sonraki görevin kabulünde reddedilebilir; standardın iki aşaması çelişir | **FIXED IN PR:** ayrı `merge-readiness`; mevcut PR için primary/support/PR author ve GitHub’a bağlı commit author/committer dışı güncel Write onayı, unresolved changes-request ve CI kontrolü |
| R03 / Yüksek | Rerun, event’teki eski base SHA’yı checkout ediyordu | main’e yeni kabul kaydı gelse de eski başarısız run aynı boş/eski kaydı okur; ekip gereksiz kilitlenir | **FIXED IN PR:** current trusted main checkout; beklenen head ve gerçek policy SHA başlangıç/sonda doğrulanır; main oynarsa yeniden çalıştırılır |
| R04 / Yüksek | #22/#30/#31 backend yolu da içerirken yalnız frontend kontrolü; #10 ve E2E #35 tek taraflı kontrol istiyordu | Backend hatası frontend CI ile görünmez; E2E doğrulaması eksik kalır | **FIXED IN PR:** #10/#22/#30/#31/#34/#35 iki uygulama kontrolünü ister; gerçek dosya yolları da ek kontrol üretir. Gerçek workflow’lar #10 tarafından geliştirilecek |
| R05 / Yüksek | #9 Java pilotu için Python backend adı; #11 kod/sözleşme teslimi için yalnız yönetim kontrolleri | Yanlış test türü veya hiç çalıştırılmayan sözleşmeler deney temelini bozabilir | **FIXED IN PR:** #9 gerçek `pilot-checks`, #11 `contract-checks`; ikisi kendi dar workflow yolunu ekleyebilir. Hazır olmayan kontrol yeşil sayılmaz; gerçek testler bu görevlerin teslimidir |
| R06 / Yüksek | #10 tüm `.github/workflows/`, uygulama işleri genel `tests/` yolunu değiştirebiliyordu | Normal modül işi kendi denetim/test altyapısını da değiştirebilir | **FIXED IN PR:** yönetim policy/script/test/workflow yolları yalnız F01-GOV; #10 yalnız uygulama CI dosyalarını açabilir. Ayrı bağımsız inceleme ve main koruması yine gereklidir |
| R07 / Yüksek | Plan ID bağımlılıkları ile issue numarası listeleri aynı olmayınca eski plan doğrulaması geçiyordu | Native grafikte bir görev, kabul denetiminde başka görev kontrol edilebilir | **FIXED IN PR:** birebir sıra/numara eşleşmesi, paket parent’ı, takım kimlikleri, öncelik/tarih/sonlu efor ve tekrar bağımlılık doğrulaması |
| R08 / Yüksek | PR yazarı, hedef branch ve API’den dönen toplam changed_files sayısı tümüyle doğrulanmıyordu | Kayıtlı işi başkası üstlenebilir veya eksik listelenen diff scope kontrolünden kaçabilir | **FIXED IN PR:** primary/support yazar; doğru repo/main; tam ve benzersiz dosya listesi; rename’in eski/yeni yolu; eksik veri güvenli reddedilir |
| R09 / Orta | Kabul kaydı türleri zayıftı; login büyük/küçük harfi ve unresolved başka review davranışı eksikti | Yanlış kayıt biçimleri, kimlik normalizasyonu veya çelişkili incelemeler kabulü bozabilir | **FIXED IN PR:** liste biçimli HTTPS kanıt, credentials’sız URL, pozitif gerçek int PR numarası; case-insensitive reviewer; ilgili PR head/merge SHA’sına bağlı CI |
| R10 / Yüksek | `backend/uploads/`, iç `private/`, symlink ve bozuk UTF-8 dosyası eski hijyen kontrolünde kaçabiliyordu | Hassas dosya/sır yayımı veya host dosyasına link üzerinden erişim riski | **FIXED IN PR:** tüm derinliklerde özel dizin kontrolü, linkleri izlememe, replacement decoding, NUL güvenli git listesi ve provider-key biçimi. Bu kontrol tam SAST/SCA değildir |
| R11 / Orta | Graph sync ilk görevleri yazdıktan sonra ilerideki beklenmeyen parent/edge’de durabiliyordu | Başarısız bir run kısmi ve açıklaması zor yönetim değişikliği bırakabilir | **FIXED IN PR:** tüm graph read-preflight, sonra yalnız beklenen eklemeler; tek concurrency grubu ve job timeout. Yazı aşamasındaki ağ hatası hâlâ kısmi sonuç bırakabilir; idempotent rerun + audit gerekir |
| R12 / Orta | Plan, issue gövdesi ve elle doldurulan Project alanları için otomatik drift alarmı yoktu | Plan revizyonlarında sahip/tarih/efor ve graph sessizce farklılaşabilir | **PARTIALLY FIXED:** read-only `audit_plan.py` 31 görevin owner/body/parent/edge’ini denetler; manuel main workflow’u hazır. Kişisel Project hücreleri ayrı haftalık kontrol ister; otomatik Project senkronizasyonu iddia edilmez |
| R13 / Yüksek | F08-UI #21 API sözleşmesini bekliyordu, gerçek frontend ortamı #10 native önkoşul değildi | Ortam gecikirse UI entegrasyon hedefi bağımlılıklar açısından yanıltıcı görünür | **FIXED IN PR + LIVE EDGE VERIFIED:** #21 → #10 eklendi; 31 görev korunur, graph 53’ten 54 edge’e çıkar. Mock geliştirme serbest; gerçek entegrasyon ortam kabulünü bekler |
| R14 / Yüksek | 10 doğrudan edge aynı hedef haftada; #26→#27→#29→#30 zinciri aynı hafta. Review dağılımı İsmail 13, Burkay 12, Cafer 6, Taha/Alperen 0 | Küçük gecikme doğrulama ve akademik teslim zincirini sıkıştırır; reviewer kuyruğu oluşur | **OPERATIONAL ACTION:** haftalık gerçek kapasite, kalan efor ve reviewer SLA belirleyin; daha küçük PR’ler; uygun bağımsız alternatif reviewer; P1’i önce erteleyin. Onaysız kapasite/tarih veya reviewer değişikliği uydurulmadı |
| R15 / Yüksek | Toplam görev midpoint 493 kişi-saat; review/yeniden çalışma dahil değil. Cafer’in bazı haftaları 22–26 tahmini saat | Eşit olmayan iş yükü, ders ve diğer işler bilinmeden gerçek kapasite sanılabilir | **PARTIALLY FIXED:** workload’a review duyarlılık tablosu eklendi; görev başı 1–2 saat yalnız varsayım. 31–62 ek saat ilk yaklaşımıdır; birden çok PR/revizyonla artar. Ekip haftalık kullanılabilirliğini bildirmeli |
| R16 / Yüksek | #25 gerçek provider ve #19 GPU/runtime erişimi doğrulanmamış; ikisi resource-blocked | Kaynak yoksa gerçek patch/Local AI ölçümü üretilemez. Mock başarı olarak raporlanırsa akademik sonuç bozulur | **RESOURCE DECISION:** #8 kapsamında provider/veri aktarım izni/kota/harcama tavanını erken kararlaştırın; #25 P0 için kritik, Local AI P1. M3 CUDA kabul edilmez; 4090 erişimi/uyumu ayrıca ölçülür. Ücretli çağrı başlatılmadı |
| R17 / Orta | Kabul/issue/review durumu yeşil run’dan sonra değişebilir; review gönderimi PR-target gate’i kendiliğinden yeniden çalıştırmaz | Eski yeşil/başarısız sonuç yanlış yorumlanabilir | **DOCUMENTED RESIDUAL:** review/CI bitince ve merge öncesinde iki gate’i rerun; kabul iptalini reviewed main değişikliğiyle yapıp branch’i güncelleyin. Canlı durumları sürekli izleyen write-token otomasyonu kurulmadı; anlık atomiklik iddia edilmez |
| R18 / Yüksek | Platform tasarımı, ürün güvenliği ve deneylerin çoğu henüz uygulanmamış | Governance testlerini davranış eşdeğerliği, sandbox güvenliği veya araştırma başarısı sanmak yanlış güven üretir | **ACCEPTANCE PLAN:** V0/test hash immutability, gerçek pilot build/test, sandbox escape/network/resource testleri, iki ürün onayı, birleşik regresyon, tüm başarısız denemeleri koruyan deney protokolü; mevcut task kabul kriterlerine göre doğrulanacak |

| R19 / Orta | Önceki DOCX “Kesin tarihler ders takvimiyle teyit edilecektir” diyor; eski bağımsız MD hâlâ “GitHub üzerinde hiçbir değişiklik yapılmamıştır” ve H1–H12 içeriyor | Eski dosyayı ekiple paylaşmak teslim tarihi, ilerleme ve kaynak önceliği konusunda karışıklık yaratır | **DOCUMENTED / SOURCE CONTROL:** gerçek uygulama için dated GitHub Roadmap ve task-plan esas alınır; eski dosyalar tarihsel tasarım kaynağıdır. Kullanıcının ikinci aşamada DOCX’i yeniden yazmama talimatı korundu; akademik teslim güncellemesinde ayrıca eşleştirilmeli |

## Tekrarlanmış kontroller

- 27 eski test korundu; toplam **81** test yerelde geçiyor. Yeni regresyonlar mevcut PR review/CI eksikliği, support onayı, canlı head/policy değişimi, eksik diff, governance path koruması, graph/kayıt türleri, secrets/symlink ve preflight yan etkilerini sınar. (81 tests pass locally; hosted execution is linked on PR #38.)
- Denetim başlangıcında altı native parent listesinden 31 gerçek child toplandı; her birinin blocked_by listesi API’den okundu: **53 edge**. Owner/body/date/effort/parent/edge snapshot denetimi hata vermedi. Eklenen tek entegrasyon önkoşulu #21 → #10, [başarılı native sync](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39870483114) sonrasında API’den [11, 10] olarak doğrulandı; graph artık 54 edge içerir.
- PR #38 eski head SHA’sında hosted governance checks başarılı; check-run kayıtları gerçek head SHA’sıyla eşleşti. Yeni düzeltmenin son SHA’sı için CI yeniden çalıştırılır; eski run yeni kodun kanıtı değildir.
- Dört workflow YAML’ı yerel YAML parser ile çözümlendi. `security-checks` ve doküman link kontrolü çalıştırıldı. Token’lar read-only; issue graph sync ayrı owner-only issues-write işlemidir. Hiçbir privileged job PR head kodunu yürütmez.
- Board’da beş görünüm ve Roadmap başlangıç/hedef alanları doğru kaldı. Item closed / PR merged → Testing; Auto-close issue Off. Bunlar issue/PR kabulünü otomatik doğrulamaz.
- Rulesets ekranı boş; Branches ekranında mevcut koruma kuralı yok. API üzerinden branch protection okuması integration yetkisiyle 403 döndüğü için bu sonuç tarayıcı arayüzünden doğrulandı; 403 “koruma yok” kanıtı olarak kullanılmadı.

## Çözüm sırası ve karar sahipleri

1. **Bu PR’nin güncel düzeltmesi:** Cafer hazırlığı; Burkay bağımsız review. Owner merge izni kayıtlıdır; Burkay’ın son SHA onayı gelmeden merge edilmez. (Independent review remains required.)
2. **GitHub aktivasyonu:** Merge sonrası gerçek canary: dependency yok/var, sonradan kabul + eski-event rerun, destek geliştiricisi onayı, bağımsız onay, failed/missing app CI, head/policy hareketi. Başarılı beş check ancak canlı kanıtından sonra required yapılır. (Activate only proven checks.)
3. **İlk sprint:** #8 kapsam/kaynak kararı; #11 executable contract-checks; #9 Java pilot-checks; #10 pinned backend/frontend + gerçek CI. Stub/no-test “başarısı” kabul edilmez. (Build actual evidence before downstream integration.)
4. **Haftalık operasyon:** owner/support/reviewer kapasitesi; read-only Live plan audit; Project hücrelerinin registry ile karşılaştırılması; anahtarsız onaylı kanıt; bağımlı hedeflerin yeniden planlanması. (Review actual capacity and drift.)
5. **P0 teslim:** #35 E2E hedef 13 Aralık; kaynak ve kapasite yetmezse P1 kesilir. P1 sınırı 20 Aralık, paket 27 Aralık, 28–31 Aralık rezerv, son teslim **1 Ocak 2027**, saat bilinmiyor. (No invented delivery hour.)

## Araştırma ve mimari için kalan doğrulama soruları

Bunlar eksik ürün kodunda mevcut hata bulunduğu iddiası değil, gerçekleştirilmeden başarı ilan edilmemesi gereken kabul kapılarıdır:

- Başlangıç Java pilotu gerçekten build/test geçiyor mu; ≥12 refactoring görevi hedefi gerçek bulgularla sağlanıyor mu? Test seti ve V0 hash’i kilitli mi?
- Upload traversal/symlink/arşiv bombası, worker network/host mount/process/resource sınırları ve timeout senaryoları gerçekten reddediliyor mu?
- Aynı sınıf/ortak arayüz/read-write çatışmaları ve uncertain bağımlılıklar konservatif sıralanıyor mu? Üç bağımsız işte paralellik kanıtı var mı?
- Candidate geçtiğinde combined validation yine tam çalışıyor mu; failed/unverified çıktıya Validated ZIP engeli var mı?
- Secrets maskeleme, kaynak yorumlarından prompt injection, harici veri aktarımı izni ve model çıktısı JSON/path/test guard’ları backend’de mi uygulanıyor?
- Tool/rule/model/prompt/context/test sürümleri sabit mi; false positive/negative ve başarısız denemeler paydadan atılmıyor mu? Ders kapsam onayı ve TÜBİTAK başvurusu birbirinden ayrı mı?

## Sınırlar ve resmî dayanak

Bu audit kendi hazırladığı kontrolü onaylayıp merge etmez; canlı koruma testi yokken “GitHub merge’i engelliyor” demez. Repository Write sahiplerinin kasıtlı olarak head workflow’larını manipüle etmesine karşı yalnız check-name eşleşmesi tam güvenlik sınırı değildir. Trusted-main gate, dar policy yolları, bağımsız CODEOWNERS incelemesi ve aktif branch protection birlikte gerekir; public kişisel repo için kurumsal zorunlu-workflow güvencesi iddia edilmez.

GitHub resmî belgelerine göre required check güncel SHA’da ve son yedi günde başarılı olmalıdır; workflow_dispatch-only job’ları required PR check olarak sayılmaz; pull_request_target ve pull_request_review uygun event türleri arasındadır. Bu nedenle manual audit required listesine eklenmedi, henüz canlı çalışmamış merge-readiness de etkin koruma gibi sunulmadı.

- [Required status checks troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
- [Workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [Collaborator permission endpoint](https://docs.github.com/en/enterprise-cloud@latest/rest/collaborators/collaborators)
- [Tek görev ve bağımlılık planı](DEVELOPMENT_ROADMAP.md)
- [Kesin kabul ve rerun prosedürü](DEPENDENCY_MANAGEMENT.md)
- [Haftalık iş/review yükü](TEAM_WORKLOAD.md)

GitHub hesabına bağlı olmayan commit kimlikleri ve serbest metin Co-authored-by kayıtları otomatik olarak güvenilir hesapla eşleştirilemez; reviewer’ın gerçek katkısızlığı ayrıca insan incelemesiyle teyit edilmelidir. Tüm beş üye aynı teslimde kod yazdıysa bağımsız review için ekip içinde katkısız bir kişi kalmayabilir; görevleri küçük tutup bir inceleyiciyi geliştirmeden ayrı bırakın.
