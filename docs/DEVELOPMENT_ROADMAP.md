# Takvim ve görev haritası / Roadmap

Last plan refresh: 2026-10-22. Final deadline **2027-01-01**, no assumed hour. Existing work began in September; audited main contains 8 Markdown files and 10 historical commits, not an implemented application. The older 12-week relative schedule is superseded by these dates without rewriting the academic DOCX.

| Window | Goal |
|---|---|
| Oct 21–Nov 1 | Scope, contracts, governance, immutable pilot and reproducible environment |
| Nov 2–15 | Safe input, Java adapter, quality/sandbox/baseline, context and independent UI |
| Nov 16–29 | Deterministic security, selection integration, conflict DAG and real patches |
| Nov 30–Dec 13 | Candidate/retry/combined validation, basic reports and verified P0 E2E |
| Dec 7–20 | Capacity permitting: Local AI, Python, JS/TS, advanced reports; separate P1 evidence |
| Dec 14–20 | Frozen experiments, failure-inclusive analysis and limitations |
| Dec 21–27 | Reproducible package, demo and academic delivery preparation |
| Dec 28–31 | Contingency, fixes and regression; no new planned features |
| Jan 1, 2027 | Course submission; exact time unconfirmed |

## Research work packages

| Work package | Owner | Tracker | Phases |
|---|---|---|---|
| İP1 — Deney temeli ve platform sözleşmeleri | @caferkilinc | [#2](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/2) | F00–F03 |
| İP2 — Dil çekirdeği ve başlangıç kalite/davranış ölçümü | @cakarburkayy | [#3](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/3) | F04–F06 |
| İP3 — Güvenlik inceleme hattı ve Local AI | @Yaman-A-E | [#4](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/4) | F07A/B |
| İP4 — İlk onay ve bağımlılığa duyarlı paralel refactoring | @Yaman-A-E | [#5](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/5) | F08–F10 |
| İP5 — Kanıta dayalı doğrulama ve nihai sürüm | @ismail-cevik | [#6](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/6) | F11–F13 |
| İP6 — Çok dilli genişleme ve deneysel değerlendirme | @tahaugurtoyran | [#7](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/7) | F14–F15 |

## Technical tasks and mandatory integration edges

Date windows include contract/mock development; same-week prerequisites must be accepted before downstream integration, not necessarily before independent coding starts. Supporting developers cover contract implementation in parallel. If prerequisite acceptance slips, dependent merge targets must be rescheduled.

| Plan / Issue | Owner; support; reviewer | P | Start → target | Effort range | Mandatory prerequisites |
|---|---|---|---|---|---|
| `F00-PLAN` [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 6–10 h | None |
| `F00-V0` [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` |
| `F01-GOV` [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-21 → 2026-10-25 | 8–12 h | None |
| `F01-ENV` [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) `F01-GOV` |
| `F02-CONTRACT` [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 10–16 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` |
| `F02-STATE` [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT`, [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) `F01-ENV` |
| `F03-INPUT` [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 14–22 h | [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) `F02-STATE` |
| `F04-JAVA` [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P0 | 2026-11-02 → 2026-11-08 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT`, [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT` |
| `F05-QUALITY` [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) | @cakarburkayy; @caferkilinc; @ismail-cevik | P0 | 2026-11-09 → 2026-11-15 | 16–24 h | [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` |
| `F06-SANDBOX` [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 18–26 h | [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) `F01-ENV`, [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT` |
| `F06-TESTS` [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17) | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-09 → 2026-11-15 | 12–18 h | [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) `F00-V0`, [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA`, [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) `F06-SANDBOX` |
| `F07A-SCAN` [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) | @cakarburkayy; @ismail-cevik; @caferkilinc | P0 | 2026-11-16 → 2026-11-22 | 14–22 h | [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) `F05-QUALITY`, [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT` |
| `F07B-PILOT` [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19) | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P1 | 2026-10-26 → 2026-11-01 | 6–10 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` |
| `F07B-LOCAL` [#20](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/20) | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 14–20 h | [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19) `F07B-PILOT`, [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) `F07A-SCAN` |
| `F08-UI` [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21) | @tahaugurtoyran; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-15 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT` , [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) `F01-ENV` |
| `F08-INTEGRATE` [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22) | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 8–12 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21) `F08-UI`, [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) `F05-QUALITY`, [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17) `F06-TESTS`, [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) `F07A-SCAN` |
| `F09-CONTEXT` [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) | @Yaman-A-E; @cakarburkayy; @caferkilinc | P0 | 2026-11-09 → 2026-11-15 | 18–26 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT`, [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` |
| `F09-SCHED` [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 10–16 h | [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) `F09-CONTEXT` |
| `F10-PATCH` [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25) | @Yaman-A-E; @caferkilinc; @ismail-cevik | P0 | 2026-11-23 → 2026-11-29 | 18–26 h | [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT`, [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22) `F08-INTEGRATE`, [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) `F09-SCHED` |
| `F11-VALIDATE` [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) | @ismail-cevik; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 18–26 h | [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17) `F06-TESTS`, [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25) `F10-PATCH`, [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) `F07A-SCAN` |
| `F11-RETRY` [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27) | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P0 | 2026-11-30 → 2026-12-06 | 6–10 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) `F11-VALIDATE` |
| `F12-REVIEW` [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) | @tahaugurtoyran; @ismail-cevik; @cakarburkayy | P0 | 2026-11-16 → 2026-11-29 | 12–18 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21) `F08-UI`, [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT` |
| `F12-FINAL` [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29) | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-12-01 → 2026-12-06 | 14–22 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) `F11-VALIDATE`, [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27) `F11-RETRY`, [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) `F12-REVIEW` |
| `F13-BASIC` [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) | @tahaugurtoyran; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 10–16 h | [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29) `F12-FINAL`, [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) `F05-QUALITY` |
| `F13-ADV` [#31](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/31) | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 10–16 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC` |
| `F14-PY` [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32) | @cakarburkayy; @ismail-cevik; @caferkilinc | P1 | 2026-12-07 → 2026-12-13 | 14–22 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC`, [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` |
| `F14-JSTS` [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P1 | 2026-12-14 → 2026-12-20 | 18–26 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC`, [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` |
| `F14-MIX` [#34](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/34) | @tahaugurtoyran; @cakarburkayy; @ismail-cevik | P1 | 2026-12-18 → 2026-12-20 | 6–10 h | [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32) `F14-PY`, [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) `F14-JSTS` |
| `F15-P0` [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35) | @ismail-cevik; @tahaugurtoyran; @caferkilinc | P0 | 2026-12-07 → 2026-12-13 | 16–24 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC` |
| `F15-EXPERIMENT` [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) | @caferkilinc; @Yaman-A-E; @ismail-cevik | P0 | 2026-12-14 → 2026-12-20 | 18–26 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35) `F15-P0`, [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` |
| `F15-HANDIN` [#37](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/37) | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-12-21 → 2026-12-27 | 10–16 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35) `F15-P0`, [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) `F15-EXPERIMENT` |

## Critical P0 integration chain

Scope/contracts + governance/environment → state → safe input → Java adapter/quality and sandbox/baseline → deterministic scan/approval integration → context/conflict scheduling → real provider patch → candidate validation/retry → combined final validation → basic report → P0 E2E → experiments → packaging. Contract-ready UI/context work proceeds on independent branches. Resource access for real provider #25 must be settled early; unapproved paid calls are not an automatic fallback.

Local AI #19/#20 and P1 adapters never block Java P0. Finish dates are planning targets, not claims of progress. The issue edge list above is the exact graph; native edges are created from the same registry.

## First sprint: October 21–25

- Cafer: #1 governance PR and #8 scope/protocol/resource decisions; #11 contracts with Burkay support after scope approval. No claim that all three are already implemented.
- Burkay: support #8/#11 and review #1; prepare adapter contract examples.
- İsmail: support #1, review #8/#11 and prepare the #10 reproducibility checklist.
- Alperen: review context/provider interfaces with consumers; identify #19 runtime/GPU evidence needs, without paid services.
- Taha: review API/approval UI contracts and prepare mock fixtures; #21 implementation starts after contract acceptance.

Weekly capacity is declared rather than assumed. If Cafer cannot cover the first-week estimate, Burkay co-develops schemas and the #11 merge target moves before downstream integration.
