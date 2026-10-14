#!/usr/bin/env python3
"""Offline declared-record integrity only; no model call, semantic grading or Beta authorization."""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

REQUIRED = ('schema_version','run_id','case_id','candidate_commit','platform','model','skill_sources',
            'isolation','execution','inputs','outputs','expected_behavior','forbidden_behavior','status',
            'adjudication','quality','artifacts','missing_evidence','redactions')
STATUS = ('PASS','FAIL','PARTIAL','NOT TESTED')
KINDS = ('input','raw_output','transcript','call_evidence','skill','docx','pdf','image','other')
ORIGINS = ('USER_INPUT','MODEL_OUTPUT','PLATFORM_EXPORT','EXPECTED_REFERENCE','SELF_REPORTED','SYNTHETIC')


def require(value,message):
    if not value:
        raise ValueError(message)


def check(record, directory, index_bytes=False):
    data=copy.deepcopy(record)
    require(all(key in data for key in REQUIRED),'required record fields missing')
    require(data['schema_version']=='1.0','unsupported schema_version')
    require(re.fullmatch(r'[A-Za-z0-9_-]+',data['run_id'] or '') is not None,'invalid local run ID')
    require(data['case_id'] and re.fullmatch(r'[0-9a-f]{40}',data['candidate_commit'] or ''),'case/candidate SHA required')
    require(data['status'] in STATUS,'invalid status')
    for section,keys in (('platform',('product','surface','evidence')),('model',('name','version','reasoning_effort','evidence'))):
        require(all(data[section].get(key) for key in keys),f'{section} provenance missing')
    require(data['expected_behavior'] and data['forbidden_behavior'],'expected/forbidden required')
    require(all(isinstance(data[key],list) for key in ('skill_sources','inputs','outputs','artifacts','missing_evidence','redactions')),'record collections must be arrays')
    isolation=data['isolation']
    require(all(k in isolation for k in ('fresh_conversation','history_or_memory_disabled','evidence','contamination')),'isolation fields missing')
    require(all(isolation[k] is None or isinstance(isolation[k],bool) for k in ('fresh_conversation','history_or_memory_disabled')),'invalid isolation flags')
    require(isinstance(isolation['contamination'],list) and isolation['evidence'],'isolation disclosure missing')
    artifacts={}
    base=Path(directory).resolve()
    for artifact in data['artifacts']:
        require(artifact['id'] and artifact['id'] not in artifacts,'duplicate/empty artifact ID')
        require(artifact['kind'] in KINDS and artifact['origin'] in ORIGINS,'artifact kind/origin invalid')
        name=artifact['path']
        require(isinstance(name,str) and name and '\\' not in name,'unsafe artifact path')
        relative=PurePosixPath(name)
        require(not relative.is_absolute() and '..' not in relative.parts and str(relative)==name,'unsafe artifact path')
        path=base/name
        require(path.resolve().is_relative_to(base) and path.is_file(),f'artifact unavailable or outside run: {name}')
        content=path.read_bytes()
        digest=hashlib.sha256(content).hexdigest()
        size=len(content)
        require(artifact.get('sha256') in (None,digest),'artifact hash mismatch; do not overwrite altered evidence')
        require(artifact.get('byte_size') in (None,size),'artifact size mismatch')
        if index_bytes:
            artifact.update(sha256=digest,byte_size=size)
        else:
            require(artifact.get('sha256')==digest and artifact.get('byte_size')==size,'hash/size missing; use --index-bytes on original evidence')
        artifacts[artifact['id']]=artifact
    def reference(value):
        require(isinstance(value,dict) and value.get('artifact_id') in artifacts and value.get('anchor'),'evidence artifact ID/anchor missing')
        return artifacts[value['artifact_id']]
    for item in data['inputs']:
        require(reference(item)['kind']=='input','input must reference saved input artifact')
    for item in data['outputs']:
        artifact=reference(item)
        require(artifact['kind'] in ('raw_output','transcript','docx','pdf','image'),'output artifact kind invalid')
    for source in data['skill_sources']:
        require(all(source.get(k) for k in ('name','path','commit','read_status')),'Skill provenance fields missing')
        require(source['artifact_id'] in artifacts and artifacts[source['artifact_id']]['kind']=='skill','Skill artifact missing')
        require(source['commit']=='UNVERIFIED' or re.fullmatch(r'[0-9a-f]{40}',source['commit']),'invalid Skill commit')
        require(source['read_status'] in ('FULL','PARTIAL','UNVERIFIED','NOT_READ'),'invalid read_status')
        if source['read_status']=='FULL':
            reference(source['evidence_anchor'])
    execution=data['execution']
    require(execution['kind'] in ('PLANNED','HUMAN_MODEL_RUN','SYNTHETIC','STATIC'),'invalid execution kind')
    require(isinstance(execution['actual_model_call'],bool),'actual_model_call must be boolean')
    require(execution['kind']=='HUMAN_MODEL_RUN' or not execution['actual_model_call'], 'static/synthetic/planned record cannot declare a live model call')
    actual=execution['kind']=='HUMAN_MODEL_RUN' and execution['actual_model_call']
    raw=any(artifacts[o['artifact_id']]['origin'] in ('MODEL_OUTPUT','PLATFORM_EXPORT') and artifacts[o['artifact_id']]['kind'] in ('raw_output','transcript') for o in data['outputs'])
    if not actual or not raw:
        require(data['status']=='NOT TESTED','no actual model call/raw output: status must be NOT TESTED')
    if actual:
        require(reference(execution['call_evidence'])['kind'] in ('call_evidence','transcript','image'), 'call evidence kind invalid')
    if data['status']!='NOT TESTED':
        require(data['inputs'] and data['outputs'],'tested record needs saved inputs/outputs')
        judgment=data['adjudication']
        require(judgment.get('verifier') and judgment.get('basis') and judgment.get('evidence_anchors'),'tested record needs verifier/basis/evidence')
        for anchor in judgment['evidence_anchors']:
            reference(anchor)
    if data['status']=='PASS':
        require(isolation['fresh_conversation'] is True and not isolation['contamination'],'PASS requires uncontaminated fresh conversation')
    quality=data['quality']
    require(all(k in quality for k in ('docx_generation','source_fidelity','visual_qa','visual_evidence','pages_reviewed')),'quality fields missing')
    require(all(quality[k] in STATUS for k in ('docx_generation','source_fidelity','visual_qa')),'invalid quality status')
    if not actual or not raw:
        require(all(quality[k]=='NOT TESTED' for k in ('docx_generation','source_fidelity','visual_qa')),
                'planned/synthetic run cannot claim model output quality tested')
    if quality['docx_generation']!='NOT TESTED':
        require(any(artifacts[o['artifact_id']]['kind']=='docx' and artifacts[o['artifact_id']]['origin']=='MODEL_OUTPUT' for o in data['outputs']),
                'DOCX generation claim requires actual declared model DOCX output')
    if quality['visual_qa']!='NOT TESTED':
        require(isinstance(quality['pages_reviewed'],list) and quality['pages_reviewed'] and all(type(page) is int and page>0 for page in quality['pages_reviewed']),
                'visual claim requires actual pages reviewed')
        require(reference(quality['visual_evidence'])['kind'] in ('pdf','image'), 'visual evidence requires PDF/page image')
    require(data['adjudication'].get('basis') and isinstance(data['adjudication'].get('limitations'),list),'adjudication disclosure missing')
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path)
    parser.add_argument('--index-bytes',action='store_true')
    args=parser.parse_args()
    try:
        data=check(json.loads(args.record.read_text()),args.record.parent,args.index_bytes)
        if args.index_bytes:
            path=args.record.with_name(args.record.stem+'.indexed.json')
            with path.open('x',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
                f.write('\n')
            print(f'Indexed actual bytes to {path}; judgment unchanged: {data["status"]}')
        print('INTEGRITY CHECK ONLY: declared record/files consistent; model behavior, authenticity, visual QA and Beta approval NOT VERIFIED')
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(f'FAIL: {e}',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    sys.exit(main())
