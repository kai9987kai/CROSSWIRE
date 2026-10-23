'use strict';
const $ = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const state = {catalog:null, active:null, completed:null, busy:false};
const labels = {fixed:'Fixed sequence',random:'Seeded random',disagreement:'Mapping disagreement',task:'Task disagreement',aalpy:'AALpy learner',counterexample:'Counterexample-guided (CEGP)',entropy:'Shannon entropy (InfoGain)',ec2:'Equivalence class edge cutting (EC2)',branching:'Adaptive within-query branching',robust:'Robust sequence across survivors',adaptive:'Adaptive policy across survivors',risk_controlled:'Risk-controlled version space',one_best:'One best survivor',unique:'Unique mapping only',fit:'Best fit (forced baseline)',identity:'Identity (forced baseline)',abstain:'Always abstain',oracle:'Oracle (privileged)',open_loop:'Open loop (unshielded)',shielded:'Dynamic runtime shield',recovery:'Simplex recovery shield',replan:'Receding-horizon replanning shield'};
function element(tag, text, cls){const node=document.createElement(tag);if(text!==undefined&&text!==null)node.textContent=String(text);if(cls)node.className=cls;return node;}
function svgElement(tag, attrs={}, text){const node=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,String(value)));if(text!==undefined)node.textContent=String(text);return node;}
function readable(value){if(value===null||value===undefined)return 'Not available';if(typeof value==='boolean')return value?'Yes':'No';if(typeof value==='object')return JSON.stringify(value);return String(value);}
function number(value){return typeof value==='number'&&Number.isFinite(value)?Number.isInteger(value)?String(value):value.toLocaleString(undefined,{maximumFractionDigits:4}):'—';}
function word(value){return Array.isArray(value)?value.length?value.join(' · '):'∅':'—';}
function notice(message,success=false){$('notice').textContent=message;$('notice').className=`notice${success?' success':''}`;$('notice').hidden=false;}
async function request(path,options={}){let response;try{response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...options.headers}});}catch{throw new Error('The local HTTP worker is unavailable. Start the CROSSWIRE server and open its HTTP address.');}let data;try{data=await response.json();}catch{throw new Error(`The server returned a non-JSON response (${response.status}). Check that this is the CROSSWIRE HTTP server.`);}if(!response.ok){const error=new Error(typeof data.error==='string'?data.error:typeof data.message==='string'?data.message:`Request failed (${response.status}): ${readable(data.error||data)}`);error.status=response.status;throw error;}if(!data||typeof data!=='object')throw new Error('The server response is malformed.');return data;}
function lock(){const busy=state.busy||!!state.active;$('run-button').disabled=busy||!state.catalog;$('study-button').disabled=busy||!state.catalog;$('import-button').disabled=busy;$('replay-button').disabled=busy||!state.completed;$('export-button').disabled=!state.completed;}
function optionList(id,items,fallback){const select=$(id);select.replaceChildren();for(const entry of items){const value=typeof entry==='string'?entry:entry.id||entry.name||entry.value;if(!value)continue;const option=element('option',typeof entry==='object'?entry.label||labels[value]||value:labels[value]||value);option.value=value;select.append(option);}if(fallback&&Array.from(select.options).some(o=>o.value===fallback))select.value=fallback;}
function familyDescription(){const current=state.catalog?.families.find(entry=>entry.id===$('family').value);$('family-description').textContent=current?.description||'';$('family-scope').textContent=(current?.scope||'Scope unspecified').replaceAll('_',' ');}
function config(){const data={};for(const name of ['family','implementation','policy','admission','execution_mode','split','probe_safety'])if($(name))data[name]=$(name).value;for(const name of ['seed','budget','horizon','risk_tolerance'])if($(name))data[name]=Number($(name).value);if(data.family==='generated_protocol')data.instance_seed=Number($('instance_seed').value);data.anchors=$('anchors').checked;data.temporal=$('temporal').checked;data.escalate=$('escalate')?$('escalate').checked:false;return data;}
function studyConfig(){
    const selected=config(),adaptive=selected.admission==='adaptive';
    const spec={families:[selected.family],seeds:[selected.seed,(selected.seed+1)%4294967296],
        budgets:[...new Set([Math.floor(selected.budget/2),selected.budget])],
        policies:adaptive?[selected.policy]:selected.policy==='fixed'?['task','fixed']:[selected.policy,'fixed'],admissions:adaptive?['robust','adaptive']:[selected.admission],
        implementations:[selected.implementation],anchors:selected.anchors,split:selected.split,
        horizon:selected.horizon,temporal:selected.temporal,escalate:selected.escalate,execution_mode:selected.execution_mode,
        probe_safety:selected.probe_safety,risk_tolerance:selected.risk_tolerance};
    if(selected.family==='generated_protocol')spec.instance_seeds=[selected.instance_seed,(selected.instance_seed+1)%4294967296];
    return spec;
}
function selectedPolicy(){return $('policy').value;}
function syncControls(){
    const adaptive=$('admission').value==='adaptive',risk=$('admission').value==='risk_controlled';
    $('instance_seed').disabled=$('family').value!=='generated_protocol';
    if(adaptive&&!['shielded','recovery'].includes($('execution_mode').value))$('execution_mode').value='shielded';
    if($('escalate')&&$('escalate').checked){$('temporal').checked=false;$('temporal').disabled=true;}
    else if($('temporal')){$('temporal').disabled=false;}
    for(const option of $('execution_mode').options)option.disabled=adaptive&&!['shielded','recovery'].includes(option.value);
    $('risk_tolerance').disabled=!risk;if(!risk)$('risk_tolerance').value='0';
    const incompatible=$('policy').value==='aalpy'&&(adaptive||$('temporal').checked||$('escalate').checked||$('probe_safety').value==='model_safe');
    $('policy').setCustomValidity(incompatible?'AALpy requires unrestricted calibration, a static model without escalation, and a non-adaptive admission rule.':'');
    $('admission-help').textContent=adaptive?'Adaptive policies choose actions from the observed branch. Shielded or recovery execution is required.':risk?'Admission limits hazardous and goal-failing fractions of the surviving candidates under uniform weighting.':'Robust admission requires a sequence satisfying the contract for every surviving mapping. Other rules provide different guarantees; forced baselines are diagnostic.';
    if(!state.catalog)return;
    const spec=studyConfig(),runs=spec.seeds.length*spec.budgets.length*spec.policies.length*spec.admissions.length*(spec.instance_seeds?.length||1);
    $('study-description').textContent=`${runs} runs · ${spec.families[0]}${spec.instance_seeds?` · structural seeds ${spec.instance_seeds.join(' / ')}`:''} · label seeds ${spec.seeds.join(' / ')} · call budgets ${spec.budgets.join(' / ')}. ${adaptive?'Robust vs adaptive admission, using the selected probe policy.':`${labels[selectedPolicy()]||selectedPolicy()} vs ${$('policy').value==='fixed'?'task':'fixed'} probes, using the selected admission rule.`} Horizon ${spec.horizon} · ${spec.split} · ${labels[spec.execution_mode]||spec.execution_mode} · ${spec.probe_safety==='model_safe'?'model-safe':'unrestricted'} calibration${risk?` · candidate tolerance ${spec.risk_tolerance}`:''}. Label seeds and target engines are nuisance repeats of structural parents.`;
    if($('study-protocol'))$('study-protocol').textContent=JSON.stringify(spec,null,2);
}
async function startJob(path,body,kind='run'){
    if(state.active||state.busy)return;
    state.busy=true;lock();
    try{
        const job=await request(path,{method:'POST',body:JSON.stringify(body)});
        if(typeof job.id!=='string')throw new Error('The worker did not return a valid job ID.');
        state.active={id:job.id,kind};$('notice').hidden=true;$('job-panel').hidden=false;
        $('job-message').textContent=`${kind==='replay'?'Scientific replay':kind==='import'?'Import and scientific replay':'Experiment'} queued`;
        $('job-status').textContent=job.status||'QUEUED';$('job-progress').removeAttribute('value');$('cancel-button').disabled=false;
        poll(job.id);
    }catch(error){notice(error.message);}finally{state.busy=false;lock();}
}
async function poll(id){
    if(state.active?.id!==id)return;
    try{
        const job=await request(`/api/runs/${encodeURIComponent(id)}`);
        if(typeof job.status!=='string')throw new Error('The worker returned a malformed job status.');
        $('job-status').textContent=job.status;
        const p=job.progress||{};$('job-message').textContent=p.message||'Running experiment';
        if(Number.isFinite(p.total)&&p.total>0&&Number.isFinite(p.current)){$('job-progress').max=p.total;$('job-progress').value=Math.max(0,Math.min(p.current,p.total));}
        else $('job-progress').removeAttribute('value');
        if(job.status==='COMPLETE'){
            const kind=state.active.kind;
            if(kind==='replay'){
                const replay=job.result||{};
                notice(`${replay.valid===true?'Replay verified':'Replay verification failed'}: ${readable(replay.message)}${replay.scientific_hash?` · ${replay.scientific_hash}`:''}`,replay.valid===true);
            }else{
                if(!job.result||!['crosswire-result-v1','crosswire-study-v1'].includes(job.result.schema))throw new Error('The completed job has no supported result.');
                state.completed={id,result:job.result};render();
                if(kind==='import')notice('Receipt loaded after its exact scientific replay matched.',true);
            }
            state.active=null;$('job-panel').hidden=true;lock();return;
        }
        if(['FAILED','CANCELLED'].includes(job.status)){
            state.active=null;$('job-panel').hidden=true;
            notice(job.status==='CANCELLED'?'Job cancelled. The last completed result is preserved.':`Job failed: ${readable(job.error||'No details supplied')}. The last completed result is preserved.`);
            lock();return;
        }
        if(!['RUNNING','QUEUED'].includes(job.status))throw new Error(`Unsupported job status: ${job.status}`);
        setTimeout(()=>poll(id),450);
    }catch(error){
        if(error.status===404){state.active=null;$('job-panel').hidden=true;notice('The worker no longer has this job. The last completed result is preserved.');lock();return;}
        notice(`${error.message} Tracking job ${id}; retrying. The last completed result is preserved.`);
        setTimeout(()=>poll(id),2000);
    }
}
function panel(title,subtitle){const section=element('section',null,'panel section-panel');const header=element('div',null,'section-heading');header.append(element('h3',title));if(subtitle)header.append(element('span',subtitle));section.append(header);return section;}
function keyValues(values){const dl=element('dl',null,'kv');for(const [key,value] of Object.entries(values)){dl.append(element('dt',key.replaceAll('_',' ')),element('dd',readable(value)));}return dl;}
function rawDetails(title,value){const details=element('details',null,'fineprint');details.append(element('summary',title),element('pre',JSON.stringify(value,null,2),'raw'));return details;}
function table(headers,rows){const wrap=element('div',null,'table-scroll');const tab=element('table');const head=element('thead'),tr=element('tr');for(const header of headers){const cell=element('th',header);cell.scope='col';tr.append(cell);}head.append(tr);const body=element('tbody');for(const row of rows){const line=element('tr');for(const [index,value] of row.entries()){const cell=element('td');if(headers[index]==='Conditions')cell.className='conditions-cell wrap';cell.append(value instanceof Node?value:document.createTextNode(readable(value)));line.append(cell);}body.append(line);}tab.append(head,body);wrap.append(tab);return wrap;}
function drawGraph(reference){const transitions=reference?.transitions;if(!Array.isArray(transitions)||!transitions.length)return element('p','No supported reference transition table is available.','fineprint');const count=transitions.length;const svg=svgElement('svg',{viewBox:'0 0 560 400',class:'graph',role:'img','aria-label':'Reference state transition graph. Edge labels show input and output symbol IDs.'});svg.append(svgElement('title',{},'Reference transducer; edge label input / output'));const defs=svgElement('defs'),marker=svgElement('marker',{id:'arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});marker.append(svgElement('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#4d6e7d'}));defs.append(marker);svg.append(defs);const positions=transitions.map((_,i)=>({x:280+145*Math.cos(2*Math.PI*i/count-Math.PI/2),y:200+132*Math.sin(2*Math.PI*i/count-Math.PI/2)}));const grouped=new Map();transitions.forEach((row,from)=>{if(!Array.isArray(row))return;row.forEach((cell,input)=>{if(!Array.isArray(cell)||!positions[cell[0]])return;const key=`${from}:${cell[0]}`;if(!grouped.has(key))grouped.set(key,{from,to:cell[0],labels:[]});grouped.get(key).labels.push(`${input}/${cell[1]}`);});});for(const edge of grouped.values()){const a=positions[edge.from],b=positions[edge.to];let path,lx,ly;if(edge.from===edge.to){path=`M ${a.x-14} ${a.y-18} C ${a.x-68} ${a.y-88}, ${a.x+68} ${a.y-88}, ${a.x+14} ${a.y-18}`;lx=a.x;ly=a.y-66;}else{const dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy),nx=-dy/d,ny=dx/d;const bend=grouped.has(`${edge.to}:${edge.from}`)?25:7;path=`M ${a.x+dx/d*26} ${a.y+dy/d*26} Q ${(a.x+b.x)/2+nx*bend} ${(a.y+b.y)/2+ny*bend} ${b.x-dx/d*28} ${b.y-dy/d*28}`;lx=(a.x+b.x)/2+nx*(bend+12);ly=(a.y+b.y)/2+ny*(bend+12);}svg.append(svgElement('path',{d:path,class:'edge','marker-end':'url(#arrow)'}),svgElement('text',{x:lx,y:ly,class:'label','text-anchor':'middle'},edge.labels.join('  ')));}positions.forEach((p,i)=>{svg.append(svgElement('circle',{cx:p.x,cy:p.y,r:24,class:`node${i===(reference.initial||0)?' initial':''}`}),svgElement('text',{x:p.x,y:p.y+5,class:'state','text-anchor':'middle'},`s${i}`));});return svg;}
function metricValue(value){return typeof value==='number'?number(value):value===null||value===undefined?'—':readable(value);}
function metricCards(values){
    const grid=element('div',null,'metric-grid');
    for(const [title,value] of values){const card=element('div',null,'metric');card.append(element('b',metricValue(value)),element('span',title));grid.append(card);}
    return grid;
}
function renderPolicy(decision,deployment){
    const section=panel('Contingent policy','OBSERVATION-DEPENDENT ACTIONS');
    section.append(element('p','Each action is chosen before its raw output is observed. Follow the matching output branch to the next action or STOP. Highlighted nodes show the path actually executed.','fineprint'));
    const executed=Array.isArray(deployment.executed_word)?deployment.executed_word:[],outputs=Array.isArray(deployment.outputs)?deployment.outputs:[];
    let shown=0,truncated=false;
    function visit(node,depth,onPath,raw){
        const item=element('li');
        if(shown>=200){truncated=true;item.append(element('span','More nodes in the exported receipt','fineprint'));return item;}
        shown++;
        if(raw!==undefined)item.append(element('div',`Observe raw ${raw}`,'policy-observation'));
        if(!node||typeof node!=='object'){item.append(element('span','Unsupported policy node','fineprint'));return item;}
        const stop=node.stop===true,selected=onPath&&(stop?deployment.complete===true&&depth===executed.length:executed[depth]===node.action);
        item.append(element('span',stop?'STOP':`Action ${readable(node.action)}`,`policy-node${stop?' policy-stop':''}${selected?' policy-executed':''}`));
        if(!stop){
            const children=element('ul');
            for(const [symbol,child] of Object.entries(node.branches||{})){
                if(shown>=200){truncated=true;break;}
                children.append(visit(child,depth+1,onPath&&executed[depth]===node.action&&String(outputs[depth])===symbol,symbol));
            }
            if(children.childNodes.length)item.append(children);
        }
        return item;
    }
    const tree=element('ul',null,'policy-tree');tree.setAttribute('aria-label','Policy actions and raw observation branches');tree.append(visit(decision.policy,0,true));section.append(tree);
    if(truncated)section.append(element('p','Showing up to 200 policy nodes. Export contains the full tree.','fineprint'));
    return section;
}
function renderDeployment(deployment){
    const section=panel('Executed deployment','TARGET ACTION / RAW OUTPUT');
    const executed=Array.isArray(deployment.executed_word)?deployment.executed_word:[],outputs=Array.isArray(deployment.outputs)?deployment.outputs:[];
    section.append(element('p',`Executed: ${word(executed)} · Observed: ${word(outputs)}`,'word'));
    if(executed.length)section.append(table(['Step','Target action','Raw output','Survivors after observation'],executed.map((action,i)=>[i+1,action,outputs[i]??null,deployment.survivor_history?.[i+1]??null])));
    else section.append(element('p','No target actions were executed.','fineprint'));
    section.append(keyValues({complete:deployment.complete,mode:labels[deployment.mode]||deployment.mode,shield_status:deployment.shield_status,intervened:deployment.intervened,deployment_calls:deployment.target_calls}));
    if(deployment.replanned)section.append(element('p',`Replanned online: safe detours were synthesized during deployment (${deployment.replan_count||1} replans).`,'fineprint'));
    for(const reason of deployment.reasons||[])section.append(element('p',reason,'fineprint'));
    if(deployment.replan_events?.length)section.append(rawDetails('Replanning events',deployment.replan_events));
    if(deployment.error)section.append(rawDetails('Deployment error',deployment.error));
    return section;
}
function renderCertificate(cert,search){
    const c=cert||{},section=panel('Public model evidence',c.valid===true?'CERTIFICATE CHECKED':'CERTIFICATE UNVERIFIED');
    section.append(element('p',c.scope||'Public model evidence only; does not authenticate private audits or target execution.','fineprint'));
    section.append(keyValues(Object.fromEntries(Object.entries(c).filter(([k,v])=>v===null||typeof v!=='object'))));
    if(c.model_diagnostics)section.append(renderModelDiagnostics(c.model_diagnostics));
    if(c.elimination?.length&&c.kind==='unresolved')section.append(rawDetails('Minimal contradiction core & elimination cascade',c.elimination));
    section.append(rawDetails('Full certificate and search bounds',{certificate:c,search}));
    return section;
}
function renderModelDiagnostics(diagnostic){
    const section=element('div',null,'model-diagnostics'),refuted=diagnostic.inclusion_status==='REFUTED';
    section.append(element('p',`Model inclusion: ${refuted?'REFUTED':'UNKNOWN'}`,`model-inclusion${refuted?' refuted':''}`));
    section.append(element('p',refuted?'Public observations refute every enabled model class. The certificate and the private execution audit make separate claims.':'Actual model inclusion remains UNKNOWN. Compatible finite observations and an admitted plan leave unobserved behavior and semantic validity unresolved.','fineprint'));
    if(diagnostic.scope)section.append(element('p',diagnostic.scope,'fineprint'));
    if(Array.isArray(diagnostic.enabled_classes))section.append(element('p',`Enabled classes: ${diagnostic.enabled_classes.join(' / ')}`,'fineprint'));
    for(const [name,model] of Object.entries(diagnostic.classes||{})){
        const block=element('div',null,'diagnostic-class'),events=Array.isArray(model.events)?model.events:[],status=model.inclusion_status||(model.candidate_count===0?'REFUTED':'UNKNOWN');
        block.append(element('h4',`${name.replaceAll('_',' ')} model class · ${status}`),keyValues({surviving_candidates:model.candidate_count,scored_symbols:model.scored_symbols,unscored_symbols:model.unscored_symbols}));
        const first=model.first_refutation;
        if(first){
            block.append(element('p',first.kind==='anchor'?`First refutation: conflicting anchor for raw ${readable(first.raw)} and semantic ${readable(first.semantic)}.`:`First refutation: probe ${Number.isInteger(first.probe_index)?first.probe_index+1:'—'}, step ${number(first.step)}${first.word_prefix?` · prefix ${word(first.word_prefix)}`:''}. Observed raw output ${readable(first.observed_output)} had no support among ${number(first.survivors_before)} prior candidates.`,'fineprint'),rawDetails('First public refutation witness',first));
        }else block.append(element('p','No refutation was observed in this finite transcript.','fineprint'));
        block.append(element('h4','Prediction support timeline'),element('p','Predicted output counts use the candidates available before that output was observed. Counts describe finite candidate support. UNSCORED events follow class refutation.','fineprint'));
        if(events.length)block.append(table(['Probe','Step','Action','Predicted raw output : count','Observed raw','Before','After','Support'],events.slice(0,200).map(event=>[Number.isInteger(event.probe_index)?event.probe_index+1:null,event.step,event.action,Object.entries(event.predicted_output_counts||{}).map(([symbol,count])=>`${symbol}: ${count}`).join(' · ')||'—',event.observed_output,event.survivors_before,event.survivors_after,event.prediction_status])));
        else block.append(element('p','No observed symbols are available for prediction scoring.','fineprint'));
        if(events.length>200)block.append(element('p',`Showing 200 of ${events.length} events. The exported receipt contains the complete timeline.`,'fineprint'));
        section.append(block);
    }
    const reset=diagnostic.reset_consistency||{};
    section.append(element('p',`Reset-prefix consistency: ${reset.status||'UNKNOWN'}. Repeated prefixes test only the observed reset behavior.`,'fineprint'));
    if(reset.first_conflict){const conflict=reset.first_conflict;section.append(element('p',`First reset-prefix conflict: ${word(conflict.word_prefix)} across probes ${Number.isInteger(conflict.previous_probe_index)?conflict.previous_probe_index+1:'—'} and ${Number.isInteger(conflict.probe_index)?conflict.probe_index+1:'—'}.`,'fineprint'),rawDetails('Reset-prefix conflict witness',conflict));}
    const blindSpots=Array.isArray(diagnostic.blind_spots)?diagnostic.blind_spots:[];
    if(blindSpots.length){const list=element('ul',null,'fineprint diagnostic-notes');for(const warning of blindSpots)list.append(element('li',warning));section.append(element('h4','Public evidence blind spots'),list);}
    return section;
}
function renderCalibration(result){
    const cfg=result.configuration||{},check=result.evidence_certificate?.calibration_safety||{},acquisition=result.decision?.calibration||{};
    const mode=check.mode||acquisition.mode||cfg.probe_safety||'unrestricted',section=panel('Calibration safety',mode==='model_safe'?'ALL SURVIVING MODELS':'UNRESTRICTED PROBES');
    const reasons={NO_ELIGIBLE_SAFE_PROBE:'Calibration stopped because no eligible model-safe probe remained.',CONTRACT_READY:'Calibration stopped once the contract decision was ready.',CALL_CAP:'Calibration reached the configured target-call cap.',MODEL_CONTRADICTED:'The observations contradicted every model in the checked class.',NO_INFORMATIVE_PROBE:'No informative probe remained within the configured search.',INTERFACE_ERROR:'Calibration stopped after a target interface error.',NOT_REQUESTED:'Calibration was not requested.',CLASSICAL_BASELINE:'Calibration was performed by the classical learner.'};
    section.append(element('p',mode==='model_safe'?'Each dispatched probe must avoid the contract hazard under every surviving model before execution. Safety is conditional on the target belonging to that model class and on truthful anchors.':'Probes were selected without a requirement to avoid the contract hazard across all surviving models. The private audit reports any hazardous calibration events separately.','fineprint'));
    section.append(keyValues({mode,checked_probes:check.checked_probes??null,public_check_passed:check.safe??null,model_class:check.model_class||acquisition.safety_model_class||null,stop_reason:acquisition.stop_reason||null}));
    if(acquisition.stop_reason)section.append(element('p',reasons[acquisition.stop_reason]||acquisition.stop_reason,'fineprint'));
    if(check.scope||acquisition.scope)section.append(element('p',check.scope||acquisition.scope,'fineprint'));
    return section;
}
function renderRun(result,container){
    const d=result.decision||{},audit=result.audit||{},ambiguity=result.ambiguity||{},metrics=result.metrics||{},dep=result.deployment||{};
    const statusGrid=element('div',null,'status-grid'),dec=element('section',null,`panel status-card${d.admitted?' good':''}`);
    dec.append(element('p','02 / FROZEN DECISION','eyebrow'),element('h2',d.status||'Status unavailable'),element('div',d.admitted?(d.policy?'Branching policy admitted':`Plan: ${word(d.word)}`):'No plan admitted','word'),element('p',`Admission: ${labels[result.configuration?.admission]||result.configuration?.admission||'—'} · ${readable(d.candidate_count??ambiguity.map_count)} candidate mappings`));
    if(d.reason)dec.append(element('p',d.reason,'fineprint'));
    if(d.search)dec.append(element('p',`Policy search: ${number(d.search.expanded_nodes)} / ${number(d.search.node_limit)} nodes · ${d.search.complete===true?'complete within bounds':'incomplete within bounds'}`,'fineprint'));
    if(d.risk_metrics)dec.append(element('p',d.admitted?`Uniformly weighted candidate fractions: hazardous ${number(d.risk_metrics.hazard_risk)} (allowed ${number(d.risk_metrics.tolerance)}) · goal-satisfying ${number(d.risk_metrics.goal_rate)}. These are finite model counts, not calibrated probabilities of harm.`:`Candidate-fraction admission: no plan selected; candidate rates are undefined. Configured tolerance ${number(result.configuration?.risk_tolerance??d.risk_metrics.tolerance)} under uniform candidate weighting.`,'fineprint'));
    if(d.escalation?.escalated)dec.append(element('p','Escalated to temporal model class after static refutation','fineprint'));
    if(d.structural_contradiction)dec.append(element('p','Structural contradiction: no adapter in static or temporal class explains trace','fineprint'));
    const outcome=element('section',null,`panel status-card${audit.contract_satisfied===true?' good':audit.contract_satisfied===false?' bad':''}`);
    outcome.append(element('p','03 / PRIVATE AUDIT','eyebrow'),element('h2',audit.contract_satisfied===true?'Contract satisfied':audit.contract_satisfied===false?'Contract violated':'No execution outcome'),element('p',`Goal reached: ${readable(audit.goal_success)} · Deployment hazard: ${readable(audit.hazard)}`),element('p',`Calibration: ${number(audit.calibration_hazardous_probes)} hazardous probes. Oracle feasible: ${readable(audit.oracle_feasible)}.`),element('p','Audit truth is withheld during acquisition.','fineprint'));
    if(dep.intervened)outcome.append(element('p',`Shield intervened: ${readable(dep.reasons?.[0]||dep.shield_status)}`,'fineprint'));
    if(audit.hazard_averted===true)outcome.append(element('p','Private counterfactual audit reports a deployment hazard averted.','fineprint'));
    if(dep.recovery?.succeeded)outcome.append(element('p','Simplex fail-safe recovery successfully executed without hazard.','fineprint'));
    if(dep.replanned)outcome.append(element('p',`Replanned online: ${dep.replan_count||1} safe detours executed.`,'fineprint'));
    statusGrid.append(dec,outcome);container.append(statusGrid);
    container.append(metricCards([['Surviving mappings',ambiguity.map_count],['Observation classes',ambiguity.observational_classes],['Contract classes',ambiguity.contract_classes],['Acquisition calls',metrics.target_calls],['Deployment calls',metrics.deployment_calls??dep.target_calls],['Total target calls',metrics.total_calls??(Number.isFinite(metrics.target_calls)&&Number.isFinite(dep.target_calls)?metrics.target_calls+dep.target_calls:null)],['Hazardous calibration probes',audit.calibration_hazardous_probes],['Deployment hazard',audit.hazard],['Deployment mode',labels[result.configuration?.execution_mode]||result.configuration?.execution_mode]]));
    if(d.policy)container.append(renderPolicy(d,dep));
    if(d.admitted||dep.executed_word?.length)container.append(renderDeployment(dep));
    container.append(renderCertificate(result.evidence_certificate||d.certificate,d.search));
    const top=element('div',null,'two-panels'),reference=panel('Reference model','INPUT / OUTPUT');
    reference.append(drawGraph(result.reference),element('p',`Goal symbol ${readable(result.contract?.goal)} · Hazard symbol ${readable(result.contract?.hazard)} · Horizon ${readable(result.contract?.horizon)}. Amber ring marks the initial state.`,'fineprint'));
    const candidates=Array.isArray(result.candidates)?result.candidates:[],mapping=panel('Candidate mappings',`${candidates.length} RETAINED`),temporal=result.configuration?.temporal||candidates.some(c=>c.delay);
    mapping.append(element('p','Input maps: target → reference. Output maps: reference → target. IDs are opaque symbols.','fineprint'));
    if(temporal)mapping.append(element('p','Delay is measured in steps. Initial output is the reference symbol buffered by a delayed adapter; its output map gives the first raw symbol.','fineprint'));
    if(candidates.length)mapping.append(table(temporal?['ID','Input map','Output map','Delay','Initial output']:['ID','Input map','Output map'],candidates.slice(0,200).map(c=>temporal?[c.id,word(c.input_map),word(c.output_map),c.delay||0,c.delay?c.init_output:'—']:[c.id,word(c.input_map),word(c.output_map)])));
    else mapping.append(element('p','No candidate mappings retained.','fineprint'));
    if(candidates.length>200)mapping.append(element('p','Showing the first 200 mappings; export contains the full result.','fineprint'));
    top.append(reference,mapping);container.append(top);
    const probes=Array.isArray(result.probes)?result.probes:[],timeline=panel('Acquisition evidence',`${probes.length} PROBES`),list=element('ol',null,'timeline');
    timeline.append(element('p',`The private audit counted ${number(audit.calibration_hazardous_probes)} hazardous calibration probes. These costs are separate from deployment hazards; successful deployment does not erase acquisition harm.`,'fineprint'));
    probes.forEach((probe,i)=>{const item=element('li'),info=element('div',null,'probe-code');info.append(element('div',`in  ${word(probe.word)}`),element('div',`out ${word(probe.outputs)}`,'muted'));const count=element('div',null,'probe-count');count.append(element('div',`${Array.isArray(probe.survivors_before)?probe.survivors_before.length:readable(probe.survivors_before)} → ${Array.isArray(probe.survivors_after)?probe.survivors_after.length:readable(probe.survivors_after)}`),element('div',probe.complete===true?'Complete':'Incomplete'));if(probe.safety)count.append(element('div',probe.safety.model_safe===true?`Model-safe · ${number(probe.safety.candidate_count)} maps`:'Safety check unavailable'));item.append(element('span',String(i+1).padStart(2,'0'),'probe-index'),info,count);list.append(item);});
    timeline.append(probes.length?list:element('p','No acquisition probes were executed.','fineprint'));container.append(timeline);
    container.append(renderCalibration(result));
    const bottom=element('div',null,'two-panels'),cost=panel('Measured work','SEPARATE COST DOMAINS');cost.append(keyValues(metrics));
    const checks=panel('Audit & assumption checks','POST-DECISION');checks.append(keyValues(Object.fromEntries(Object.entries(audit).filter(([,v])=>v===null||typeof v!=='object'))));
    if(audit.counterexample)checks.append(element('p',`Counterexample: ${word(audit.counterexample)}`,'fineprint'));
    checks.append(rawDetails('Full audit, including finite assumptions',audit));bottom.append(cost,checks);container.append(bottom);
    const receipt=panel('Receipt & scientific boundary');receipt.append(element('p','This result concerns the configured synthetic family and finite planning horizon. Mapping ambiguity, observable equivalence, and contract equivalence are different quantities. A successful private audit does not establish real-world safety or unrestricted semantic understanding.','fineprint'),keyValues({scientific_hash:result.scientific_hash,target_id:result.target_id,parent_instance_id:result.parent_instance_id}));
    if(result.instance_design)receipt.append(element('h4','Structural instance design'),keyValues({structural_instance_seed:result.configuration?.instance_seed,generator:result.instance_design.generator,dynamics_hash:result.instance_design.dynamics_hash,sampling_unit:result.instance_design.sampling_unit}),rawDetails('Instance design metadata',result.instance_design));
    receipt.append(rawDetails('Configuration and baseline',{configuration:result.configuration,baseline:result.baseline}));container.append(receipt);
}
function conditionLabel(cfg={}){
    return `${cfg.split||'development'} · H${cfg.horizon??4} · ${labels[cfg.execution_mode||'open_loop']||cfg.execution_mode} · anchors ${cfg.anchors?'on':'off'} · temporal ${cfg.temporal?'on':'off'} · escalation ${cfg.escalate?'on':'off'} · ${cfg.probe_safety==='model_safe'?'model-safe':'unrestricted'} probes · candidate tolerance ${number(cfg.risk_tolerance??0)}`;
}
function intervalText(interval){return Array.isArray(interval)&&interval.length===2&&interval.every(value=>typeof value==='number'&&Number.isFinite(value))?interval.map(number).join(' to '):null;}
function targetEventMetric(metric={}){
    const interval=intervalText(metric.interval),unknown=Number.isInteger(metric.unknown_targets)?metric.unknown_targets:0;
    return `${number(metric.events)} / ${number(metric.targets)} targets · observed rate ${number(metric.rate)}${interval?` · interval ${interval}`:''}${unknown?` · ${unknown} unknown target${unknown===1?'':'s'}${typeof metric.possible_rate==='number'?` · possible rate ${number(metric.possible_rate)}`:''}`:''}`;
}
function renderReliability(reliability){
    const section=panel('Independent-target reliability','CONDITIONAL SYNTHETIC INFERENCE');
    section.append(element('p','Structural parents are the sampling units. Label seeds and target engines are nuisance repeats; additional requests do not increase the number of independent targets. Intervals require the worker\'s independence and sampling assumptions within each condition.','fineprint'),element('p','Unknown target outcomes remain unresolved. A zero observed hazard count leaves uncertainty about unseen targets and unexecuted deployments. Conditional selective harm conditions on admission, using equal-target means.','fineprint reliability-note'));
    for(const row of reliability){
        const block=element('article',null,'reliability-stratum'),useful=row.target_average_useful_coverage||{},usefulInterval=intervalText(useful.interval),hasInterval=intervalText(row.target_any_deployment_hazard?.interval)||intervalText(row.target_any_calibration_hazard?.interval)||usefulInterval;
        block.append(element('h4',`${row.family||'Unknown family'} / ${row.method||'Unknown method'} / B${row.budget??'?'}`),element('p',conditionLabel(row),'fineprint'),keyValues({Requests:row.requests,'Parent clusters':row.parent_clusters,'Independent parents':row.independent_parents,...(row.unique_nuisance_requests!==undefined?{'Unique nuisance cells':row.unique_nuisance_requests}:{}),...(row.structural_seed_collisions?{'Structural seed collisions':row.structural_seed_collisions}:{})}));
        const metrics=element('div',null,'reliability-metrics');
        for(const [title,value] of [['Any deployment hazard',targetEventMetric(row.target_any_deployment_hazard)],['Any calibration hazard',targetEventMetric(row.target_any_calibration_hazard)],['Target-average useful coverage',`${number(useful.estimate)}${usefulInterval?` · interval ${usefulInterval}`:''}`]]){
            const metric=element('div',null,'reliability-metric');metric.append(element('h5',title),element('p',value));metrics.append(metric);
        }
        block.append(metrics,keyValues({'Conditional selective harm':row.conditional_selective_harm===null||row.conditional_selective_harm===undefined?'Undefined':number(row.conditional_selective_harm)}),element('p',`Inferential sampling eligible: ${readable(row.inference_eligible)}${row.inference_reason||row.reason?` · ${readable(row.inference_reason||row.reason).replaceAll('_',' ')}`:''}${hasInterval&&typeof row.confidence==='number'?` · ${number(row.confidence*100)}% pointwise intervals`:''}.`,'fineprint'));section.append(block);
    }
    for(const scope of new Set(reliability.map(row=>row.scope).filter(Boolean)))section.append(element('p',scope,'fineprint'));
    section.append(rawDetails('Inspect target-level reliability',reliability));return section;
}
function renderStudy(result,container){
    const rows=Array.isArray(result.rows)?result.rows:[],summary=Array.isArray(result.summary)?result.summary:[],intro=panel('Paired study','SERVER-COMPUTED SUMMARY');
    intro.append(element('p',`${rows.length} run results. Rates and paired comparisons below come from the worker. Declined plans have no execution outcome; selective harm is undefined when no plan was admitted. Calibration hazards are counted independently of deployment outcomes.`,'fineprint'));
    const protocol=result.protocol||{};
    intro.append(keyValues({families:protocol.families,...(protocol.instance_seeds?{structural_instance_seeds:protocol.instance_seeds}:{}),label_seeds:protocol.seeds,budgets:protocol.budgets,probe_policies:protocol.policies,admissions:protocol.admissions,parent_clusters:new Set(rows.map(row=>row.parent_instance_id)).size}));
    intro.append(element('p',`Conditions: ${conditionLabel({...rows[0]?.configuration,...protocol})}`,'fineprint'));container.append(intro);
    if(Array.isArray(result.reliability)&&result.reliability.length)container.append(renderReliability(result.reliability));
    if(summary.length){
        const plot=panel('Useful coverage by method','SERVER SUMMARY'),height=Math.max(140,summary.length*36+30),svg=svgElement('svg',{viewBox:`0 0 720 ${height}`,class:'study-chart',role:'img','aria-label':'Worker-reported useful coverage by method, family and call budget'});
        summary.forEach((row,i)=>{const y=22+i*36,label=`${row.family??''} / ${row.method??''} / B${row.budget??'?'}`,rate=typeof row.useful_coverage==='number'&&Number.isFinite(row.useful_coverage)?row.useful_coverage:null;const text=svgElement('text',{x:0,y:y+12},label.length>44?label.slice(0,43)+'…':label);text.append(svgElement('title',{},`${label} · ${conditionLabel(row)}`));svg.append(text);if(rate!==null)svg.append(svgElement('rect',{x:290,y,width:Math.max(0,Math.min(1,rate))*330,height:16,class:'bar'}));svg.append(svgElement('text',{x:635,y:y+12},rate===null?'N/A':`${number(rate*100)}%`));});plot.append(element('p','Each bar represents one family, method, budget, and condition stratum. Exact conditions are listed in the tables.','fineprint'),svg);container.append(plot);
        const summaryTable=panel('Method outcomes','PAIRED PARENT CLUSTERS');
        summaryTable.append(element('p','Contract failures include unsuccessful admitted plans. Deployment hazards count hazardous semantic events. Hazardous calibration runs and probes measure acquisition separately.','fineprint'));
        summaryTable.append(table(['Family','Method','Budget','Conditions','Runs','Parent clusters','Admitted','Successful','Contract failures','Deployment hazards','Hazardous calibration runs','Hazardous calibration probes','Useful coverage','Selective harm'],summary.map(r=>[r.family,r.method,r.budget,conditionLabel(r),r.requests,r.parent_clusters,r.admitted,r.successful,r.harmful,r.hazardous,r.calibration_hazardous_runs,r.calibration_hazardous_probes,r.useful_coverage,r.selective_harm])));container.append(summaryTable);
        const costs=panel('Acquisition & deployment costs','MEAN CALLS PER RUN');costs.append(table(['Family','Method','Budget','Conditions','Acquisition calls','Deployment calls','Total target calls','Acquisition action steps'],summary.map(r=>[r.family,r.method,r.budget,conditionLabel(r),r.mean_target_calls,r.mean_deployment_calls,r.mean_total_calls,r.mean_target_steps])));container.append(costs);
    }
    const paired=Array.isArray(result.paired)?result.paired:[],comparisons=panel('Paired comparisons & protocol','EXPLORATORY MATCHED CONTRASTS');
    comparisons.append(element('p','Differences compare matched label seeds and implementations within each semantic parent and condition stratum. Positive values favor the first method in the contrast. The descriptive 95% interval resamples whole parents; a small number of parents cannot support a confirmatory claim. Out-of-family controls are excluded.','fineprint'));
    if(paired.length)comparisons.append(table(['Contrast','Fixed method','Budget','Conditions','Parent clusters','Matched cells','Mean difference','Descriptive 95% interval'],paired.map(p=>[p.contrast,p.fixed_admission?`admission: ${p.fixed_admission}`:`policy: ${p.fixed_policy}`,p.budget,conditionLabel(p),p.parent_clusters,p.matched_cells,number(p.mean_delta),Array.isArray(p.descriptive_95_interval)?p.descriptive_95_interval.map(number).join(' to '):null])));
    else comparisons.append(element('p','No matched in-family comparison is available for this protocol. Inspect individual outcomes and the recorded conditions.','fineprint'));
    comparisons.append(rawDetails('Inspect full paired analysis',paired),rawDetails('Inspect study protocol',result.protocol));container.append(comparisons);
    const detail=element('section',null,'study-run-detail');detail.id='study-run-detail';detail.hidden=true;detail.tabIndex=-1;detail.setAttribute('aria-label','Selected study run');
    function inspectRun(row,index,trigger){
        detail.replaceChildren();const heading=panel(`Study run ${index+1}`,`${row.configuration?.family||'Unknown family'} / LABEL ${row.configuration?.seed??'—'}${row.configuration?.instance_seed!==null&&row.configuration?.instance_seed!==undefined?` / STRUCTURE ${row.configuration.instance_seed}`:''}`),close=element('button','Close run details');close.type='button';
        close.addEventListener('click',()=>{detail.hidden=true;trigger.focus();});heading.append(element('p','The toolbar continues to export and replay the complete parent study receipt.','fineprint'),close);detail.append(heading);renderRun(row,detail);detail.hidden=false;detail.focus();detail.scrollIntoView({block:'start'});
    }
    const all=panel('Individual run receipts',`${rows.length} RUNS`);all.append(table(['Inspect','Family','Structural seed','Label seed','Budget','Policy','Admission','Conditions','Decision','Audit satisfied','Calibration hazardous probes','Deployment hazard','Acquisition calls','Deployment calls'],rows.map((r,i)=>{const button=element('button',`Inspect run ${i+1}`);button.type='button';button.addEventListener('click',()=>inspectRun(r,i,button));return [button,r.configuration?.family,r.configuration?.instance_seed??'—',r.configuration?.seed,r.configuration?.budget,r.configuration?.policy,r.configuration?.admission,conditionLabel(r.configuration),r.decision?.status,r.audit?.contract_satisfied,r.audit?.calibration_hazardous_probes,r.audit?.hazard,r.metrics?.target_calls,r.metrics?.deployment_calls??r.deployment?.target_calls];})));container.append(all,detail);
}
function render(){const result=state.completed.result;$('empty-state').hidden=true;$('result-view').hidden=false;$('result-kind').textContent=result.schema==='crosswire-study-v1'?'PAIRED STUDY RECEIPT':'EXPERIMENT RECEIPT';$('result-meta').textContent=result.schema==='crosswire-study-v1'?`Source ${result.source_hash||'unavailable'}`:`${result.configuration?.family||'Unknown family'}${result.configuration?.instance_seed!==null&&result.configuration?.instance_seed!==undefined?` / structural seed ${result.configuration.instance_seed}`:''} / label seed ${result.configuration?.seed??'—'} / ${result.configuration?.implementation||'—'}`;const content=$('result-content');content.replaceChildren();if(result.schema==='crosswire-study-v1')renderStudy(result,content);else renderRun(result,content);}
$('family').addEventListener('change',familyDescription);
$('run-form').addEventListener('input',syncControls);
$('run-form').addEventListener('change',syncControls);
$('run-form').addEventListener('submit',event=>{event.preventDefault();if($('run-form').reportValidity())startJob('/api/runs',config());});
$('study-button').addEventListener('click',()=>{syncControls();if($('run-form').reportValidity())startJob('/api/studies',studyConfig(),'study');});
$('cancel-button').addEventListener('click',async()=>{if(!state.active)return;const id=state.active.id;$('cancel-button').disabled=true;try{await request(`/api/runs/${encodeURIComponent(id)}/cancel`,{method:'POST',body:'{}'});if(state.active?.id===id)$('job-message').textContent='Cancellation requested';}catch(error){if(state.active?.id===id){notice(error.message);$('cancel-button').disabled=false;}else console.warn(`Cancellation request for previous job ${id} failed: ${error.message}`);}});
$('export-button').addEventListener('click',async()=>{if(!state.completed)return;try{const response=await fetch(`/api/runs/${encodeURIComponent(state.completed.id)}/export`);if(!response.ok)throw new Error(`Export failed (${response.status})`);const text=await response.text(),blob=new Blob([text],{type:'application/json'}),url=URL.createObjectURL(blob),a=element('a');a.href=url;a.download=`crosswire-${state.completed.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){notice(error.message);}});
$('replay-button').addEventListener('click',()=>{if(state.completed)startJob(`/api/runs/${encodeURIComponent(state.completed.id)}/replay`,{},'replay');});
$('import-button').addEventListener('click',()=>$('receipt-file').click());
$('receipt-file').addEventListener('change',async event=>{
    const file=event.target.files[0];event.target.value='';if(!file||state.active||state.busy)return;
    if(file.size>20*1024*1024){notice('Receipt exceeds the 20 MiB browser import limit.');return;}
    state.busy=true;lock();
    try{
        const text=await file.text();
        try{JSON.parse(text);}catch{throw new Error('This file is not valid JSON.');}
        state.busy=false;await startJob('/api/import',{receipt_text:text},'import');
    }catch(error){notice(`Import failed: ${error.message} The last completed result is preserved.`);}
    finally{state.busy=false;lock();}
});
async function initialize(){if(location.protocol==='file:'){notice('HTTP worker unavailable: this page was opened directly from a file. Start CROSSWIRE and open the local HTTP address.');$('connection').textContent='HTTP server required';return;}try{const catalog=await request('/api/catalog');if(!Array.isArray(catalog.families)||!Array.isArray(catalog.policies)||!Array.isArray(catalog.admissions))throw new Error('The server catalog is malformed or unsupported.');state.catalog=catalog;const defaults=catalog.defaults||{};optionList('family',catalog.families,defaults.family||'latch');optionList('policy',catalog.policies,defaults.policy||'task');optionList('admission',catalog.admissions,defaults.admission||'robust');if(catalog.execution_modes)optionList('execution_mode',catalog.execution_modes,defaults.execution_mode||'open_loop');for(const name of ['seed','budget','horizon','implementation','split','probe_safety','risk_tolerance'])if(defaults[name]!==undefined&&$(name))$(name).value=defaults[name];if($('anchors'))$('anchors').checked=defaults.anchors===true;if($('temporal'))$('temporal').checked=defaults.temporal===true;if($('escalate'))$('escalate').checked=defaults.escalate===true;familyDescription();syncControls();$('connection').textContent=`Local worker · ${catalog.version||'connected'}`;$('connection-dot').classList.add('online');lock();}catch(error){notice(error.message);$('connection').textContent='Worker unavailable';}}
initialize();
