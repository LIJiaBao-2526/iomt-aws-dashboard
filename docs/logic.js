/* Pure, testable demonstration rules and retrieval. */
(function(root){
function normalize(rows){
 if(!Array.isArray(rows)||rows.length>500)throw Error('Invalid series');
 const seen=new Set();return rows.map(r=>{
  if(!r||typeof r.heart_rate!=='number'||!Number.isFinite(r.heart_rate)||r.heart_rate<20||r.heart_rate>250||typeof r.timestamp!=='string'||!/(Z|[+-]\d\d:\d\d)$/.test(r.timestamp)||!Number.isFinite(Date.parse(r.timestamp)))throw Error('Invalid reading');
  const t=new Date(r.timestamp).toISOString();if(seen.has(t))throw Error('Duplicate timestamp');seen.add(t);return {timestamp:t,heart_rate:r.heart_rate};
 }).sort((a,b)=>a.timestamp.localeCompare(b.timestamp));
}
function triggered(rows){const last=rows.slice(-3);return last.length===3&&last.every(r=>r.heart_rate>100)&&last.slice(1).every((r,i)=>{const d=Date.parse(r.timestamp)-Date.parse(last[i].timestamp);return d>0&&d<=120000;});}
function retrieve(question,kb){return kb.map((item,i)=>({item,i,score:item.keywords.reduce((s,t)=>s+Number(question.toLowerCase().includes(t.toLowerCase())),0)})).filter(r=>r.score>0).sort((a,b)=>b.score-a.score||a.i-b.i).slice(0,3).map(r=>r.item);}
const api={normalize,triggered,retrieve};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.PulseLogic=api;
})(typeof window==='undefined'?globalThis:window);
