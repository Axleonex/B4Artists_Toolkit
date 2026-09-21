from pathlib import Path
import hashlib,json,statistics
ROOT=Path(r'X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github')
BASE=ROOT/'training/b4artists_ml/results/procedural-vertical-slice-v10'
PROTOCOL=ROOT/'training/b4artists_ml/procedural_vertical_slice_protocol_v10.json'
OUT=BASE/'aggregate.json'
if OUT.exists(): raise SystemExit(f'refusing to overwrite {OUT}')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stats(values):
 values=list(values)
 return dict(min=min(values),median=statistics.median(values),max=max(values)) if values else None
protocol=json.loads(PROTOCOL.read_text())
summary=json.loads((BASE/'summary.json').read_text())
processes=json.loads((BASE/'processes.json').read_text())
expected={(profile,task) for profile in protocol['rigs'] for task in protocol['tasks']}
reports={}
for path in BASE.glob('*/*/report.json'):
 d=json.loads(path.read_text()); reports[(d['profile'],d['task'])]=(path,d)
assert set(reports)==expected and len(processes)==len(expected)==32
assert summary['complete'] and summary['passed']==32 and summary['failed']==0
protocol_sha=sha(PROTOCOL); assert summary['protocol_sha256']==protocol_sha
runtime_files=sorted((ROOT/'b4artists_ml').glob('*.py'))
runtime_sha={p.relative_to(ROOT).as_posix():sha(p) for p in runtime_files}
rows=[]; evidence=[]
for key in sorted(expected):
 path,d=reports[key]
 assert d['complete'] and all(d['automated_gates'].values())
 assert d['protocol_sha256']==protocol_sha and d['runtime_sha256']==runtime_sha
 assert d['source_restored'] and d['save_reload_passed'] and d['anchor_payloads_unchanged']
 blend=ROOT/d['blend_path']; assert blend.is_file() and sha(blend)==d['blend_sha256']
 m=d['automated_metrics']; stages=d['stages']
 row=dict(profile=d['profile'],task=d['task'],seconds=d['seconds'],interactions=d['interaction_count'],scripted_corrections=d['scripted_correction_count'],working_set_bytes=d['memory'].get('working_set_bytes'),peak_working_set_bytes=d['memory'].get('peak_working_set_bytes'),generation_seconds=stages['generation']['seconds'],generation_step_max_seconds=stages['generation']['max_step_seconds'],contact_seconds=stages['contact_refinement']['seconds'],flight_seconds=stages.get('flight_refinement',{}).get('seconds',0.0),lifecycle_seconds=stages['lifecycle']['seconds'],priority_matrix_error=m['priority_matrix_error'],pin_residual=m['max_pin_residual'],requested_pin_error_body_fraction=m['max_requested_pin_error_body_fraction'],preflight_adjustment_body_fraction=m['max_preflight_target_adjustment_body_fraction'],sampled_stretch=m['max_sampled_limb_stretch'],contact_plane_spread_body_fraction=m['contact_plane_spread_body_fraction'],penetration_body_fraction=m['max_penetration_body_fraction'],contact_error_limb_fraction=m['contact_report']['max_after'],contact_orientation_error_radians=m['contact_report']['orientation_error_radians'],rotation_velocity_jump_rad_s=m['max_rotation_velocity_jump_rad_s'],flight_error_body_fraction=(m['flight_report'] or {}).get('max_after',0.0),contact_checks=m['contact_report']['checks'],contact_validation_frames=m['contact_report']['validation_frames'],floor_normalization_body_fraction=m['max_floor_normalization_body_fraction'],floor_normalization_corrections=m['floor_normalization_corrections'],preflight_corrections=m['preflight_target_corrections'])
 rows.append(row)
 evidence.append(dict(report=path.relative_to(ROOT).as_posix(),report_sha256=sha(path),blend=d['blend_path'],blend_sha256=d['blend_sha256']))
process_map={(r['profile'],r['task']):r for r in processes}; assert set(process_map)==expected
for key,row in process_map.items():
 assert row['complete'] and row['host_exit']==3221225477
 log=ROOT/row['log']; assert log.is_file() and sha(log)==row['log_sha256']
for row in rows:
 row['host_process_seconds']=process_map[(row['profile'],row['task'])]['seconds']
fields=['seconds','host_process_seconds','generation_seconds','generation_step_max_seconds','contact_seconds','flight_seconds','lifecycle_seconds','interactions','scripted_corrections','working_set_bytes','peak_working_set_bytes']
profiles={}
for profile in protocol['rigs']:
 subset=[r for r in rows if r['profile']==profile]
 profiles[profile]={field:stats(r[field] for r in subset if r[field] is not None) for field in fields}
 profiles[profile]['cases']=len(subset)
metric_fields=['priority_matrix_error','pin_residual','requested_pin_error_body_fraction','preflight_adjustment_body_fraction','sampled_stretch','contact_plane_spread_body_fraction','penetration_body_fraction','contact_error_limb_fraction','contact_orientation_error_radians','rotation_velocity_jump_rad_s','flight_error_body_fraction','floor_normalization_body_fraction']
maxima={field:max(r[field] for r in rows) for field in metric_fields}
aggregate=dict(schema='procedural-vertical-slice-aggregate-v10',complete=True,automated_procedural_floor_complete=True,full_goal_complete=False,protocol=PROTOCOL.relative_to(ROOT).as_posix(),protocol_sha256=protocol_sha,cases=32,passed=32,failed=0,rigs=protocol['rigs'],tasks=list(protocol['tasks']),all_gates=protocol['automated_gates'],maxima=maxima,total_contact_checks=sum(r['contact_checks'] for r in rows),total_contact_validation_frames=sum(r['contact_validation_frames'] for r in rows),profiles=profiles,cases_detail=rows,runtime_sha256=runtime_sha,process_exit_codes=sorted(set(r['host_exit'] for r in processes)),clean_host_shutdown=False,host_shutdown_qualification='All in-process reports and durable artifacts completed; Bforartists then exited with the known post-result ucrtbase.dll access violation 3221225477. Clean shutdown remains unqualified.',evidence=evidence,unresolved=['Human visual quality is unrated.','Independent animator interaction/correction assessment is missing; scripted counts are not human effort.','No direct Cascadeur equivalent-task comparison has been run.','The runtime selected here is procedural authored-shape motion; learned motion remains unsatisfied and was not promoted.','Quadruped support remains outside this humanoid-first milestone.'])
OUT.write_text(json.dumps(aggregate,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({k:aggregate[k] for k in ('complete','cases','passed','failed','maxima','total_contact_checks','total_contact_validation_frames','process_exit_codes','full_goal_complete')},indent=2))
print('aggregate_sha256',sha(OUT))
