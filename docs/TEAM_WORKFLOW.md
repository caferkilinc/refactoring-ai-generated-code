# Team guide / Ekip çalışma rehberi

Bir görev seçin; owner/support/reviewer, scope ve bağımlılıkları okuyun. (Select a task and review ownership, scope and prerequisites.) Sözleşme hazırsa mock/fixture ile bağımsız geliştirme başlayabilir; entegrasyon için kabul edilmiş bağımlılık gerekir. (Approved contracts permit independent development; integration requires accepted prerequisites.)

## MacBook M3 / macOS

Git ve Python 3 kurulu olmalıdır. Bu kurulum yalnızca standard-library governance kontrollerini çalıştırır; henüz backend/frontend kurulum komutu yoktur. (Git and Python 3 are prerequisites; application setup belongs to #10.)

```sh
git clone https://github.com/caferkilinc/refactoring-ai-generated-code.git
cd refactoring-ai-generated-code
git switch main
git pull --ff-only origin main
git switch -c feature/11-cir-contracts
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
git add backend/core/schemas docs/contracts tests/contracts
git commit -m "feat: define CIR and adapter contracts"
git push -u origin feature/11-cir-contracts
```

`git add` örneğindeki yolları geliştirdiğiniz gerçek dosyalara uyarlayın. (Use the actual paths you implemented.) GitHub arayüzünden PR açın; `Task: #11` ve `Plan: F02-CONTRACT` satırlarını ekleyin. (Open the PR and include the matching task/plan lines.) Kendi PR'nizi tek başınıza onaylamayın; primary/support dışında belirlenen reviewer incelemeli. (The independent reviewer must approve the current revision.)

## Windows / PowerShell

```powershell
git clone https://github.com/caferkilinc/refactoring-ai-generated-code.git
Set-Location refactoring-ai-generated-code
git switch main
git pull --ff-only origin main
git switch -c feature/11-cir-contracts
py -3 -m unittest discover -s tests/governance -v
py -3 scripts/governance/check_docs.py
py -3 scripts/governance/security_check.py
git add backend/core/schemas docs/contracts tests/contracts
git commit -m "feat: define CIR and adapter contracts"
git push -u origin feature/11-cir-contracts
```

## Update and review

`git fetch origin` then `git merge origin/main` on your topic branch preserves history without force push. Resolve conflicts, rerun checks and push normally. Every code PR needs reproducible normal/error/integration evidence, current CI, independent approval and resolved conversations. Changes invalidate old approvals when the proposed protection is activated.

Cafer's governance PR goes to Burkay/İsmail for independent review. Each task names a reviewer distinct from primary/support; review is distributed rather than routed entirely through Cafer. CODEOWNERS provides alternative qualified owners, while the task's independent-review rule remains explicit.

All five currently have sufficient access for direct topic branches. If access is temporarily missing, fork the repository and open a PR from the fork. Do not elevate permissions or run fork code with write tokens to work around it. Native project ownership/editor access is distinct from repository Write; project access changes require owner review.

## Weekly planning

Use [workload estimates](TEAM_WORKLOAD.md). Declare available capacity, remaining estimate and blockers weekly; adjust support and dates in the canonical plan. Planning hours are not time sheets or compulsory equal schedules. Escalate #25 provider access before patch week and #19 GPU access before Local AI promises. Delay P1 first when P0 slips.

Application development environment, service health checks, pinned Python/Node and lockfiles are #10. Use native Apple Silicon toolchains for M3; actual CUDA/model runtime runs only on a separately verified server. No nonexistent application commands are claimed here.

## Readiness and recovery

Bağımsız inceleme ve CI bittikten sonra Dependency gate workflow’unu yeniden çalıştırın; `dependency-gate` ve `merge-readiness` birlikte geçmelidir. (Rerun both gates after review and CI complete.) Yeniden çalıştırma güncel güvenilir main politikasını okur; kaynak kodu veya kabul kaydı değiştiyse güncel main’i branch’inize alın. (Reruns refresh trusted main; update your branch after policy or acceptance changes.)

Java pilotu #9 `pilot-checks`, erken sözleşmeler #11 `contract-checks`, ortam #10 gerçek backend/frontend kontrollerini üretir. Eksik kontrolü başarılı göstermeyin. (Each task supplies real executable checks; missing checks cannot be reported as passed.)

Proje panosundaki Done yalnız planlama durumudur; kabul kaydı ve gerçek kanıt ayrıca gerekir. Haftalık Live plan audit ile issue/bağımlılık tutarlılığını, pano tarih/efor hücrelerini de ayrıca kontrol edin. (Audit live issue drift and separately compare the personal Project fields.)
