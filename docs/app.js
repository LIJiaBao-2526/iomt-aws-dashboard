/* Assigned owner: LEE Tsz Him. Dashboard and presentation controls. */
const LOCAL=['127.0.0.1','localhost'].includes(location.hostname)&&location.port==='8877';
const API=LOCAL?'/api/demo':'https://rl6z5doxlg.execute-api.us-east-1.amazonaws.com/dev/demo';
const $=id=>document.getElementById(id);let readings=[],mode='cloud',busy=false;
const fmt=(t,opts)=>new Date(t).toLocaleString('zh-HK',opts);
function selected(value){mode=value;for(const id of ['cloud','normal','high']){$(id).classList.toggle('selected',id===value);$(id).setAttribute('aria-pressed',String(id===value));}}
function render(data){readings=data;const last=data.at(-1);$('download').disabled=!last;if(!last){$('rate').textContent='—';$('average').textContent='—';$('time').textContent='—';$('date').textContent='沒有量測';$('count').textContent='0 筆量測';$('level').textContent='沒有資料';$('range').textContent='—';$('notice').classList.remove('warn');$('notice').textContent='尚未收到量測。';$('chart').setAttribute('aria-label','沒有資料');$('chart').innerHTML='<text x="380" y="140" text-anchor="middle" fill="#81929b">沒有資料</text>';$('rows').innerHTML='<tr><td colspan="3">沒有資料</td></tr>';return;}
$('rate').textContent=last.heart_rate;$('average').textContent=Math.round(data.reduce((s,r)=>s+r.heart_rate,0)/data.length);$('count').textContent=`${data.length} 筆合成量測`;$('time').textContent=fmt(last.timestamp,{hour:'2-digit',minute:'2-digit',second:'2-digit'});$('date').textContent=fmt(last.timestamp,{year:'numeric',month:'2-digit',day:'2-digit'});$('level').textContent='合成示範量測';$('range').textContent=`${data.length} 筆記錄`;
const warning=PulseLogic.triggered(data);$('notice').classList.toggle('warn',warning);$('notice').textContent=warning?'展示規則觸發：最後 3 筆心率均高於 100 bpm，且相鄰間隔不超過兩分鐘。這是預設情境提示，不是 AI 分析或醫療判斷。':'這組示範資料未觸發「最後 3 筆高於 100 bpm」規則。資料不代表真實健康狀態。';
$('rows').replaceChildren(...[...data].reverse().map(r=>{const row=document.createElement('tr');for(const t of [fmt(r.timestamp),`${r.heart_rate} bpm`,mode==='cloud'?(LOCAL?'本機資料庫合成資料':'AWS 儲存的合成資料'):'本頁情境模擬']){const cell=document.createElement('td');cell.textContent=t;row.append(cell);}return row;}));draw(data,warning);}
function draw(data,warning){const min=Math.min(40,Math.floor(Math.min(...data.map(r=>r.heart_rate))/10)*10),max=Math.max(160,Math.ceil(Math.max(...data.map(r=>r.heart_rate))/10)*10),W=760,H=285,left=45,right=20,top=15,bottom=40;const x=i=>left+i*(W-left-right)/Math.max(1,data.length-1);const y=v=>top+(max-v)*(H-top-bottom)/(max-min);const color=warning?'#be762c':'#087d6c';let s='';for(const v of Array.from({length:5},(_,i)=>Math.round(min+(max-min)*i/4)))s+=`<line x1="${left}" x2="${W-right}" y1="${y(v)}" y2="${y(v)}" stroke="#e8eef0"/><text x="30" y="${y(v)+4}" text-anchor="end" font-size="11" fill="#7b8f98">${v}</text>`;const line=data.map((r,i)=>`${i?'L':'M'} ${x(i)} ${y(r.heart_rate)}`).join(' ');s+=`<path d="${line} L ${x(data.length-1)} ${H-bottom} L ${left} ${H-bottom} Z" fill="${color}" opacity=".07"/><path d="${line}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;data.forEach((r,i)=>{s+=`<circle cx="${x(i)}" cy="${y(r.heart_rate)}" r="3.5" fill="white" stroke="${color}" stroke-width="2"/>`;if(i===0||i===data.length-1||i===Math.floor(data.length/2))s+=`<text x="${x(i)}" y="${H-13}" text-anchor="${i===0?'start':i===data.length-1?'end':'middle'}" font-size="11" fill="#7b8f98">${fmt(r.timestamp,{hour:'2-digit',minute:'2-digit'})}</text>`;});$('chart').innerHTML=s;$('chart').setAttribute('aria-label',`${data.length} 筆合成心率，最低 ${Math.min(...data.map(r=>r.heart_rate))}，最高 ${Math.max(...data.map(r=>r.heart_rate))} bpm`);}
async function load(){if(busy)return;busy=true;selected('cloud');$('refresh').disabled=true;$('connection').textContent=LOCAL?'正在讀取本機資料庫…':'正在讀取 AWS…';$('source').textContent=LOCAL?'資料來源：等待本機回應':'資料來源：等待 AWS 回應';$('dot').className='dot';render([]);try{const res=await fetch(API,{cache:'no-store',signal:AbortSignal.timeout(12000)});if(!res.ok)throw Error(`HTTP ${res.status}`);const body=await res.json();if(body.synthetic!==true||!Array.isArray(body.readings))throw Error('資料格式不符');if(mode!=='cloud')return;const valid=body.readings.every(r=>Number.isFinite(r.heart_rate)&&r.heart_rate>=20&&r.heart_rate<=250&&!Number.isNaN(Date.parse(r.timestamp)));if(!valid)throw Error('量測格式不符');render(PulseLogic.normalize(body.readings));$('dot').className='dot ok';$('connection').textContent=LOCAL?'本機資料庫讀取成功':'AWS 讀取成功';$('source').textContent=LOCAL?'資料來源：SQLite · HTTP 輸入／MQTT 橋接':'資料來源：DynamoDB · 合成歷史資料';}catch(e){if(mode==='cloud'){$('dot').className='dot fail';$('connection').textContent=LOCAL?'本機資料庫暫時無法讀取':'AWS 暫時無法讀取';$('source').textContent='可切換本頁情境展示';$('notice').textContent='雲端連線失敗，沒有以模擬資料替代雲端結果。可按重新讀取，或選擇本頁情境。';}}finally{busy=false;$('refresh').disabled=false;}}
function scenario(kind){selected(kind);const rates=kind==='high'?[76,78,81,85,94,104,109,112,116,120,118,121]:[73,75,74,77,76,79,78,76,80,79,77,78];const now=Date.now();render(rates.map((v,i)=>({heart_rate:v,timestamp:new Date(now-(11-i)*60000).toISOString()})));$('dot').className='dot';$('connection').textContent='本頁情境展示';$('source').textContent='資料來源：瀏覽器模擬 · 未寫入 AWS';}
$('refresh').addEventListener('click',load);$('cloud').addEventListener('click',load);$('normal').addEventListener('click',()=>scenario('normal'));$('high').addEventListener('click',()=>scenario('high'));$('download').addEventListener('click',()=>{if(!readings.length)return;const text='timestamp,heart_rate_bpm,source\n'+readings.map(r=>`${r.timestamp},${r.heart_rate},${mode==='cloud'?(LOCAL?'sqlite_synthetic':'aws_synthetic'):'browser_synthetic'}`).join('\n');const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='iomt-synthetic-readings.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});if(LOCAL)load();else scenario("normal");

if(LOCAL){$('cloud').textContent='本機資料庫';$('refresh').textContent='重新讀取資料';}
let poll=null;
$('live').addEventListener('change',()=>{clearInterval(poll);poll=$('live').checked?setInterval(()=>{if(mode==='cloud'&&!busy)load();},5000):null;});
let knowledgePromise=fetch('knowledge.json').then(r=>{if(!r.ok)throw Error('knowledge unavailable');return r.json();});
knowledgePromise.catch(()=>{});
$('ask-form').addEventListener('submit',async event=>{
 event.preventDefault();const q=$('question').value.trim();if(!q)return;const button=$('ask');button.disabled=true;$('answer').textContent='正在檢索…';$('citations').replaceChildren();
 try{
  const kb=await knowledgePromise;let result;
  // The local assistant summarizes the stored series, not the browser-only scenarios.
  if(LOCAL&&mode==='cloud'){
   const res=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q}),signal:AbortSignal.timeout(30000)});
   if(!res.ok)throw Error('API request failed');result=await res.json();
  }else{
   const refs=PulseLogic.retrieve(q,kb);const last=readings.at(-1);
   const summary=last?`目前顯示 ${readings.length} 筆合成量測，最新 ${last.heart_rate} bpm。`:'目前沒有量測資料。';
   result={mode:'retrieval',answer:summary+'\n'+(refs.length?refs.map(r=>r.text).join('\n'):'知識庫沒有足夠資料，請改問系統、心率規則或資料來源。'),sources:refs};
  }
  $('ai-status').textContent=result.mode==='deepseek'?'DeepSeek 已回應 · 檢索增強生成':'資料檢索模式 · 未呼叫 DeepSeek';
  $('answer').textContent=(result.provider_error?result.provider_error+'\n':'')+result.answer;
  for(const ref of result.sources){const a=document.createElement('a');a.textContent=ref.title;a.href=ref.url;a.target='_blank';a.rel='noopener';$('citations').append(a);}
 }catch(e){$('answer').textContent='問答暫時不可用，請重新嘗試。';$('ai-status').textContent='連線失敗';}
 finally{button.disabled=false;}
});
