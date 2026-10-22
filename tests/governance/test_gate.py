import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/governance'))
from gate import evaluate,verify_acceptance,validate_plan,Rejected
PLAN=json.loads((Path(__file__).resolve().parents[2]/'.github/task-plan.json').read_text())
class API:
 def __init__(self):
  self.issue={'state':'closed','state_reason':'completed'}
  self.pr={'number':101,'body':'Task: #8\nPlan: F00-PLAN','head':{'ref':'docs/8-scope','sha':'abc'},'base':{'ref':'main','repo':{'full_name':PLAN['repository']}},'merged_at':'2026-10-25T12:00:00Z','user':{'login':'caferkilinc'}}
  self.reviews=[{'user':{'login':'ismail-cevik'},'state':'APPROVED','commit_id':'abc'}]
  self.checks=[{'name':c,'status':'completed','conclusion':'success','app':{'slug':'github-actions'}} for c in PLAN['tasks'][0]['required_checks']]
  self.dependencies=[];self.files=[{'filename':'docs/DECISIONS/scope.md'}]
 def call(self,path,**kw):
  if '/collaborators/' in path:return {'permission':'write'}
  if '/pulls/' in path:return self.pr
  return self.issue
 def pages(self,path,key=None):
  for suffix,rows in [('/files',self.files),('/reviews',self.reviews),('/check-runs',self.checks),('/dependencies/',self.dependencies)]:
   if suffix in path:return rows
  raise RuntimeError('Unexpected request')
class GateTests(unittest.TestCase):
 def setUp(self):
  self.p=copy.deepcopy(PLAN);self.a=API();self.t=self.p['tasks'][0];self.r={'pr':101,'head_sha':'abc','evidence':['https://github.com/caferkilinc/refactoring-ai-generated-code/pull/101']}
 def accept(self):verify_acceptance(self.t,self.r,self.a,self.p)
 def test_accepted_evidence_passes(self):self.accept()
 def test_closed_alone_fails(self):
  with self.assertRaises(Rejected):verify_acceptance(self.t,None,self.a,self.p)
 def test_unmerged_fails(self):
  self.a.pr['merged_at']=None
  with self.assertRaises(Rejected):self.accept()
 def test_stale_sha_fails(self):
  self.r['head_sha']='old'
  with self.assertRaises(Rejected):self.accept()
 def test_stale_review_fails(self):
  self.a.reviews[0]['commit_id']='old'
  with self.assertRaises(Rejected):self.accept()
 def test_self_review_fails(self):
  self.a.reviews[0]['user']['login']='caferkilinc'
  with self.assertRaises(Rejected):self.accept()
 def test_later_changes_request_fails(self):
  self.a.reviews.append({'user':{'login':'ismail-cevik'},'state':'CHANGES_REQUESTED','commit_id':'abc'})
  with self.assertRaises(Rejected):self.accept()
 def test_failed_ci_fails(self):
  self.a.checks[0]['conclusion']='failure'
  with self.assertRaises(Rejected):self.accept()
 def test_untrusted_check_fails(self):
  self.a.checks[0]['app']['slug']='other'
  with self.assertRaises(Rejected):self.accept()
 def test_supporting_developer_approval_is_not_independent(self):
  self.a.reviews[0]['user']['login']='cakarburkayy'
  with self.assertRaises(Rejected):self.accept()
 def test_primary_approval_on_support_authored_pr_is_not_independent(self):
  self.a.pr['user']['login']='cakarburkayy';self.a.reviews[0]['user']['login']='caferkilinc'
  with self.assertRaises(Rejected):self.accept()
 def test_missing_check_fails(self):
  self.a.checks=[]
  with self.assertRaises(Rejected):self.accept()
 def test_missing_evidence_fails(self):
  self.r['evidence']=[]
  with self.assertRaises(Rejected):self.accept()
 def test_independent_branch_allowed(self):
  self.a.issue={'state':'open'}
  self.assertIn('all 0',evaluate(self.a.pr,self.p,{},self.a))
 def test_mandatory_dependency_blocks(self):
  self.a.issue={'state':'open'};self.a.pr.update(body='Task: #9\nPlan: F00-V0',head={'ref':'feature/9-pilot','sha':'def'});self.a.files=[{'filename':'experiments/pilot/Main.java'}];self.a.dependencies=[{'number':8}]
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_completed_dependency_reopens_gate(self):
  pr=copy.deepcopy(self.a.pr);pr.update(body='Task: #9\nPlan: F00-V0',head={'ref':'feature/9-pilot','sha':'def'},number=102)
  original=self.a
  class Complete(API):
   def call(self,path,**kw):return {'state':'open'} if path=='/issues/9' else original.call(path,**kw)
   def pages(self,path,key=None):
    if path=='/pulls/102/files':return [{'filename':'experiments/pilot/Main.java'}]
    if '/dependencies/' in path:return [{'number':8}]
    return original.pages(path,key)
  self.assertIn('all 1',evaluate(pr,self.p,{'8':self.r},Complete()))
 def test_native_mismatch_fails(self):
  self.a.issue={'state':'open'};self.a.dependencies=[{'number':19}]
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_api_failure_cannot_pass(self):
  self.a.call=lambda *a,**kw:(_ for _ in ()).throw(RuntimeError('API unavailable'))
  with self.assertRaises(RuntimeError):self.accept()
 def test_branch_body_disagreement_fails(self):
  self.a.pr['body']='Task: #9\nPlan: F00-PLAN'
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_unknown_issue_fails(self):
  self.a.pr.update(body='Task: #999\nPlan: F00-PLAN',head={'ref':'docs/999-other'})
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_research_scope_cannot_hide_app_code(self):
  self.a.issue={'state':'open'};self.a.files=[{'filename':'backend/app.py'}]
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_cycle_fails(self):
  self.p['tasks'][0]['dependencies']=['F00-V0']
  with self.assertRaises(Rejected):validate_plan(self.p)
 def test_p1_cannot_block_p0(self):
  self.p['tasks'][0]['dependencies']=['F07B-PILOT']
  with self.assertRaises(Rejected):validate_plan(self.p)
 def test_closed_governance_accepts_policy_maintenance(self):
  self.a.issue={'state':'closed','state_reason':'completed'}
  self.a.pr.update(body='Task: #1\nPlan: F01-GOV',head={'ref':'chore/1-acceptance','sha':'new'})
  self.a.files=[{'filename':'.github/acceptance.json'}]
  self.assertIn('all 0',evaluate(self.a.pr,self.p,{},self.a))
 def test_closed_governance_cannot_change_app(self):
  self.a.issue={'state':'closed','state_reason':'completed'}
  self.a.pr.update(body='Task: #1\nPlan: F01-GOV',head={'ref':'chore/1-acceptance','sha':'new'})
  self.a.files=[{'filename':'backend/app.py'}]
  with self.assertRaises(Rejected):evaluate(self.a.pr,self.p,{},self.a)
 def test_unknown_prerequisite_fails_closed(self):
  self.p['tasks'][0]['dependencies']=['UNKNOWN']
  with self.assertRaises(Rejected):validate_plan(self.p)
 def test_real_plan_p0_independent_of_local_ai(self):
  ids=validate_plan(self.p)
  def deps(t):
   result=set(t['dependencies'])
   for dep in t['dependencies']:result|=deps(ids[dep])
   return result
  for task in self.p['tasks']:
   if task['priority']=='P0':self.assertFalse(any(d.startswith('F07B') for d in deps(task)))
if __name__=='__main__':unittest.main()
