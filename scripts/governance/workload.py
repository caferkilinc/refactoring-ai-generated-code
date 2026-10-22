"""Reproducible weekly planning estimates; never measured working time."""
import argparse,json
from collections import defaultdict
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def report(plan):
 start=date(2026,10,21);weeks=[]
 while start<=date(2026,12,27):
  end=min(start+timedelta(days=6-start.weekday()),date(2026,12,27));weeks.append((start,end));start=end+timedelta(days=1)
 loads=defaultdict(float);active=defaultdict(set)
 for task in plan['tasks']:
  first,last=date.fromisoformat(task['start']),date.fromisoformat(task['target'])
  span=(last-first).days+1
  for i,(a,b) in enumerate(weeks):
   overlap=max(0,(min(b,last)-max(a,first)).days+1)
   if not overlap:continue
   for user,share in [(task['owner'],.7),(task['support'],.3)]:
    loads[i,user]+=task['estimated_effort']*share*overlap/span
    active[i,user].add(task['issue_number'])
 lines=['# Haftalık tahmini iş yükü / Weekly estimated effort','','70% primary / 30% support planning split. Calendar-day allocation is a distribution model, not actual hours or availability. Epic trackers add zero effort. Reviewer time is additional and must be agreed weekly. No fixed equal weekly capacity is imposed.','', '| Week | '+' | '.join(plan['team'])+' |','|---|'+'---:|'*len(plan['team'])]
 for i,(a,b) in enumerate(weeks):lines.append(f'| {a} – {b} | '+' | '.join(f'{loads[i,u]:.1f}' for u in plan['team'])+' |')
 lines+=['','## Weekly capacity review','','Each member declares available effort for the coming week. Compare with these estimates including support/review; track remaining work, blockers and actual progress. Replan dependent dates when a P0 gate slips. A total above 18 estimated person-hours is a review signal, not a mandatory capacity or overtime requirement. P1 work is the first candidate for deferral.','']
 for i,(a,b) in enumerate(weeks):
  for u in plan['team']:
   if loads[i,u]>18:lines.append(f'- {a}: @{u}: {loads[i,u]:.1f} estimated hours, tasks '+', '.join('#'+str(n) for n in sorted(active[i,u]))+'. Confirm capacity; share support or defer independent work.')
 lines+=['','December 14–20: Alperen supports the experiment protocol/data handling (#36); Burkay concentrates on JS/TS (#33). İsmail remains the independent reviewer. Taha supports P0 E2E, then academic packaging. Do not pull P1 tasks into an unresolved P0 integration week.','', 'Run `python3 scripts/governance/workload.py` after changing the canonical plan.']
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();s=report(json.loads((ROOT/'.github/task-plan.json').read_text()))
 if args.output:Path(args.output).write_text(s)
 else:print(s)
