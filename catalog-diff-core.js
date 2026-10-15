(function(root){
'use strict';
function parse(text){
  text=text.replace(/^\uFEFF/,'');
  let rows=[],row=[],cell='',quoted=false,closed=false,line=1,start=1,hadContent=false;
  const push=()=>{row.push(cell);cell='';closed=false;};
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(c!=='\r'&&c!=='\n')hadContent=true;
    if(quoted){if(c==='"'){if(text[i+1]==='"'){cell+='"';i++;}else{quoted=false;closed=true;}}else{cell+=c;if(c==='\n'||c==='\r'&&text[i+1]!=='\n')line++;}continue;}
    if(c==='"'){if(cell||closed)throw Error('Unexpected quote at line '+line);quoted=true;continue;}
    if(c===','){push();continue;}
    if(c==='\r'||c==='\n'){if(c==='\r'&&text[i+1]==='\n')i++;push();if(hadContent)rows.push({values:row,line:start});row=[];hadContent=false;line++;start=line;continue;}
    if(closed)throw Error('Unexpected text after closing quote at line '+line);
    cell+=c;
  }
  if(quoted)throw Error('Unclosed quoted field at line '+start);
  if(hadContent){push();rows.push({values:row,line:start});}
  if(!rows.length)throw Error('CSV has no header.');
  const headers=rows.shift().values;
  if(headers.some(h=>!h.trim())||new Set(headers).size!==headers.length)throw Error('Headers must be nonempty and unique.');
  for(const r of rows)if(r.values.length!==headers.length)throw Error('Column count differs at line '+r.line);
  if(rows.length>1000)throw Error('Prototype limit: 1,000 data records per file.');
  return {headers,rows};
}
function compare(a,b,keyA,keyB,pairs){
  if(!a.headers.includes(keyA)||!b.headers.includes(keyB))throw Error('Choose an identifier column in each file.');
  if(!pairs.length)throw Error('Choose at least one pair of fields to compare.');
  for(const p of pairs)if(!a.headers.includes(p.a)||!b.headers.includes(p.b))throw Error('Mapped field missing.');
  const output=[],idx=(table,key,side)=>{
    const m=new Map(),col=table.headers.indexOf(key);
    for(const r of table.rows){const k=r.values[col];if(!k||k!==k.trim()){output.push({status:'Review',key:k,reason:!k?'Blank identifier':'Identifier has outer whitespace',supplierLines:side==='supplier'?[r.line]:[],shopifyLines:side==='shopify'?[r.line]:[],differences:[]});continue;}if(!m.has(k))m.set(k,[]);m.get(k).push(r);}
    return m;
  };
  const ma=idx(a,keyA,'supplier'),mb=idx(b,keyB,'shopify');
  for(const k of new Set([...ma.keys(),...mb.keys()])){
    const aa=ma.get(k)||[],bb=mb.get(k)||[],base={key:k,supplierLines:aa.map(r=>r.line),shopifyLines:bb.map(r=>r.line),differences:[]};
    if(aa.length>1||bb.length>1){output.push({...base,status:'Review',reason:'Duplicate identifier; no match selected'});continue;}
    if(!aa.length||!bb.length){output.push({...base,status:aa.length?'Supplier only':'Shopify only',reason:'No exact identifier on the other side'});continue;}
    for(const p of pairs){const av=aa[0].values[a.headers.indexOf(p.a)],bv=bb[0].values[b.headers.indexOf(p.b)];if(av!==bv)base.differences.push({field:p.label,supplier:av,shopify:bv,blankInvolved:av===''||bv===''});}
    const blank=base.differences.some(d=>d.blankInvolved);
    output.push({...base,status:blank?'Review':base.differences.length?'Different':'Equal',reason:blank?'Blank differs from a value; meaning needs confirmation':base.differences.length?'Raw mapped values differ':'Exact key and mapped values agree'});
  }
  return output;
}
const api={parse,compare};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.CatalogDiff=api;
})(globalThis);
