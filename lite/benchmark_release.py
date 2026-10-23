"""Exact final release EXEs, sequential fresh processes, isolated settings; no physical input claims."""
import json, os, sys, subprocess, time, hashlib, argparse
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/final-performance'
sys.path.insert(0,str(ROOT/'lite'))
import psutil
from dual_soak import wait_for
from measure_process import sample, delta
from winprobe import windows, user

def run(edition, trial, label, base):
    folder=OUT/label/f'{edition}-{trial}'
    folder.mkdir(parents=True,exist_ok=False)
    config=folder/'config'; config.mkdir()
    (config/'settings.json').write_text(json.dumps({'x':500,'y':430,'paused':False}))
    exe=base/f'DSH-Pet-Lite-{edition.title()}'/f'DSH-Pet-Lite-{edition.title()}.exe'
    ready=folder/'ready.json'; metrics=folder/'paints.json'; statefile=Path(str(ready)+'.state.json')
    env=os.environ.copy(); env.pop('QT_QPA_PLATFORM',None)
    env['PATH']=os.pathsep.join([str(Path(os.environ['SystemRoot'])/'System32'),os.environ['SystemRoot']])
    command=[str(exe),'--config-dir',str(config),'--test-control','--ready-file',str(ready),'--metrics-file',str(metrics),'--seed',str(100+trial)]
    row={'edition':edition,'trial':trial,'label':label,'utc':datetime.now(timezone.utc).isoformat(),'command':command,'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'samples':[],'phases':[],'status':'RUNNING','cache_condition':'fresh process; OS file cache not flushed; OS-warm','cpu_status':'NOT RELIABLY MEASURED until cross-check'}
    start=time.perf_counter(); p=subprocess.Popen(command,cwd=os.environ['TEMP'],env=env); row['pid']=p.pid
    hwnd=None
    try:
        first=wait_for(lambda:json.loads(ready.read_text()))
        row['first_qt_paint_s']=first['paint_monotonic']-start; row['display']=first
        hwnd=wait_for(lambda:next((w['hwnd'] for w in windows(p.pid) if w['title']==f'DSH Pet Lite {edition.title()}'),None))
        def control(a,v=0):
            assert user.PostMessageW(hwnd,0x8000+77,a,v)
        def state():
            old=json.loads(statefile.read_text())['time'] if statefile.exists() else 0
            control(6)
            return wait_for(lambda:d if (d:=json.loads(statefile.read_text()))['time']>old else None)
        row['interactive_control_response_s']=time.perf_counter()-start if state() else None
        names=list(json.loads((exe.parent/'_internal/assets/manifest.json').read_text(encoding='utf-8'))['clips'])
        control(7,names.index('idle')); time.sleep(6); control(7,names.index('idle')); time.sleep(6)
        phases=[('idle','idle',22),('click','click',11),('drag','drag',11)]
        if edition=='core': phases += [('turn','action_105',11),('move','action_014',22)]
        phases += [('paused',None,5),('hidden',None,5),('restored','idle',3)]
        previous=sample(p.pid)
        for phase,clip,duration in phases:
            if clip: control(7,names.index(clip))
            else: control(1 if phase=='paused' else 3)
            initial=state(); begin=time.perf_counter()
            for second in range(duration):
                if phase=='idle' and second in (8,16):control(7,names.index('idle'))
                time.sleep(1)
                cur=sample(p.pid); row['samples'].append({'phase':phase,**cur,**delta(cur,previous)});previous=cur
            final=state(); row['phases'].append({'name':phase,'begin':begin,'end':time.perf_counter(),'initial':initial,'final':final})
            (folder/'result.json').write_text(json.dumps(row,indent=2))
            if phase in ('paused','hidden'):
                assert not final['timer_active'] and final['index']==initial['index']
            if phase=='hidden':assert final['cache_bytes']==0
        row['children']=len(psutil.Process(p.pid).children(recursive=True));assert row['children']==0
        control(5);row['exit_code']=p.wait(15);assert row['exit_code']==0
        row['status']='PASS'
    except Exception as e:
        row['status']='FAIL';row['error']=repr(e);raise
    finally:
        if p.poll() is None and hwnd:
            user.PostMessageW(hwnd,0x8000+77,5,0);p.wait(15)
        (folder/'result.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
    print(edition,trial,row['status'],row['first_qt_paint_s'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--label',default='baseline');ap.add_argument('--base',type=Path,default=ROOT/'dist/v3-release');ap.add_argument('--trials',type=int,default=3);ap.add_argument('--paired-base',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();OUT=args.output.resolve();args.base=args.base.resolve();args.paired_base=args.paired_base.resolve() if args.paired_base else None
    assert not [p.info for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower().startswith('dsh')]
    for trial in range(1,args.trials+1):
        for edition in (('core','ultra') if trial%2 else ('ultra','core')):
            variants=[(args.label,args.base)]
            if args.paired_base:
                variants=[(args.label+'-A',args.base),(args.label+'-B',args.paired_base)]
                if trial%2==0:variants.reverse()
            for label,base in variants:run(edition,trial,label,base)
