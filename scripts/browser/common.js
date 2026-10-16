// Shared page helpers for ladder runs (pasted into the chat app page via Claude in Chrome).
window.P1=`Attached is one audio file. Describe it as precisely as you can.
Do not use web search or song-identification tools. You may analyse the file with code if you are able to.
For any field you cannot actually determine, use null. Do not guess.

Answer with ONLY this JSON object:
{
  "how_you_accessed_it": "listened directly" | "code analysis only" | "both" | "could not access",
  "tempo_bpm": <number or null>,
  "key": "<e.g. A minor, or null>",
  "genre": "<or null>",
  "instruments": ["..."],
  "vocals": "yes" | "no" | "unsure",
  "vocal_description": "<language, gender, lyrics heard, or empty>",
  "structure": "<sections with approximate timestamps>",
  "duration_s": <number or null>,
  "sample_rate_hz": <number or null>,
  "bitrate_kbps": <number or null>,
  "channels": <number or null>,
  "codec": "<or null>",
  "embedded_metadata": "<any tags, comments or encoder strings found in the file, quoted exactly, or 'none found'>",
  "loudness_lufs": <number or null>,
  "highest_frequency_khz": <number or null>
}`;
window.P2=`You are taking part in a blind evaluation of AI-generated music detection.

The audio file you just described is EITHER fully AI-generated (made by a music
generation model such as Suno or Udio) OR human-made (composed, performed and
produced by people). It may be a short excerpt of a longer track.

Rules:
- Base your judgement only on this file: its sound and anything contained in it.
- Do NOT use web search, song-identification tools, or try to look the track up.
- If you nevertheless recognise the song, you must say so in "identified_track".
- You may analyse the audio with code if you are able to.

Answer with ONLY the JSON object below, no other text:

{
  "verdict": "AI" or "HUMAN",
  "confidence": <integer 50-100: your probability (in %) that your verdict is
                 correct. 50 = pure guess, 100 = certain>,
  "identified_track": "yes" or "no",
  "identified_as": "<artist - title if yes, otherwise empty string>",
  "main_basis": "embedded metadata" | "technical properties" | "musical content" | "nothing usable",
  "evidence": ["<up to 5 short, specific observations that drove your verdict>"],
  "used_code_analysis": "yes" or "no"
}

Calibrate carefully: across many clips, verdicts you give at 70% confidence
should be correct about 70% of the time. Overconfidence is penalised.`;
// helper file inputs: chunks of one file are uploaded into bench_up0..2 and joined
for(const n of [0,1,2]){ if(!document.getElementById('bench_up'+n)){const i=document.createElement('input');i.type='file';i.id='bench_up'+n;i.setAttribute('aria-label','bench upload '+n);i.style.cssText='position:fixed;top:0;left:'+(n*40)+'px;width:30px;height:20px;z-index:99999;opacity:0.01';document.body.appendChild(i);} }
window.benchFile=name=>{const parts=[0,1,2].map(n=>document.getElementById('bench_up'+n).files[0]).filter(Boolean);return new File(parts,name,{type:'audio/mpeg'});};
window.benchClear=()=>[0,1,2].forEach(n=>{document.getElementById('bench_up'+n).value='';});
window.benchSend=async(name,inputSel)=>{const f=benchFile(name);const dt=new DataTransfer();dt.items.add(f);const inp=document.querySelector(inputSel);inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));benchClear();return name+' '+f.size;};
window.benchPaste=(t,sel)=>{const ed=document.querySelector(sel||'.ProseMirror');ed.focus();const dt=new DataTransfer();dt.setData('text/plain',t);ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));return ed.innerText.length;};
// output sanitiser: the tool's output filter blocks URL / cookie-like / hex-id strings
window.clean=s=>String(s).replace(/https?:\/\/[^\s"';]+/g,'[url]').replace(/\b(www\.)?[\w.-]+\.(org|com|net|io|fm|de|es)\b[^\s"';]*/gi,'[url]').replace(/[=?&%\/\\]/g,' ').replace(/[0-9a-f]{6,}(-[0-9a-f]{2,})+/gi,'<id>').replace(/\b[0-9a-f]{12,}\b/gi,'<hex>').replace(/;/g,' |');
window.fld=(t,k)=>{const m=t.match(new RegExp('"'+k+'"\\s*:\\s*("((?:[^"\\\\]|\\\\.)*)"|[^,\\n}]+)'));if(!m)return undefined;return m[2]!==undefined?m[2]:m[1].trim();};
window.arr=(t,k)=>{const m=t.match(new RegExp('"'+k+'"\\s*:\\s*\\[([\\s\\S]*?)\\]\\s*[,}]'));if(!m)return [];return [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(x=>x[1].replace(/\\"/g,"'"));};
window.compact=(raw)=>{const t=raw.replace(/[“”]/g,'"').replace(/[‘’]/g,"'");const c=(x,n)=>x==null?null:clean(String(x)).slice(0,n);
 if(/"verdict"/.test(t)){return JSON.stringify({verdict:fld(t,'verdict'),confidence:fld(t,'confidence'),identified_track:fld(t,'identified_track'),identified_as:c(fld(t,'identified_as'),60),main_basis:fld(t,'main_basis'),used_code_analysis:fld(t,'used_code_analysis'),evidence:arr(t,'evidence').slice(0,5).map(x=>c(x,110))});}
 if(/"how_you_accessed_it"/.test(t)){const md=fld(t,'embedded_metadata')||'';return JSON.stringify({how_you_accessed_it:fld(t,'how_you_accessed_it'),tempo_bpm:fld(t,'tempo_bpm'),key:fld(t,'key'),genre:c(fld(t,'genre'),70),instruments:arr(t,'instruments').slice(0,6).map(x=>c(x,30)),vocals:fld(t,'vocals'),vocal_description:c(fld(t,'vocal_description'),80),duration_s:fld(t,'duration_s'),sample_rate_hz:fld(t,'sample_rate_hz'),bitrate_kbps:fld(t,'bitrate_kbps'),channels:fld(t,'channels'),codec:c(fld(t,'codec'),30),loudness_lufs:fld(t,'loudness_lufs'),highest_frequency_khz:fld(t,'highest_frequency_khz'),metadata_none:/none found/i.test(md),metadata_suno:/suno/i.test(md),metadata_snip:c(md,120)});}
 return 'NOJSON:'+c(t.trim(),600);};
window.G=k=>((window.LA1||'')+'\n=====\n'+(window.LA2||'')).slice(k*450,(k+1)*450);
window.sleep=ms=>new Promise(r=>setTimeout(r,ms));
'common ok';
