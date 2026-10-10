"""Benchmark-only command receipts; never installed into agent-dotfiles."""
import os,sys,subprocess,time,json,pathlib,hashlib
args=sys.argv[1:]
if args and args[0]=='--':args=args[1:]
start=time.monotonic();p=subprocess.run(args,capture_output=True)
row={'argv':args,'cwd':os.getcwd(),'elapsed_seconds':time.monotonic()-start,'exit_code':p.returncode,'stdout_bytes':len(p.stdout),'stderr_bytes':len(p.stderr),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stdout':p.stdout.decode('utf-8','backslashreplace'),'stderr':p.stderr.decode('utf-8','backslashreplace')}
r=pathlib.Path('receipt');r.mkdir(exist_ok=True)
with (r/'trace.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=True)+'\n')
sys.stdout.buffer.write(p.stdout);sys.stderr.buffer.write(p.stderr);raise SystemExit(p.returncode)
