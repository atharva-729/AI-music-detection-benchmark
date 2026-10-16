// Gemini driver (load common.js first). Temporary chat, app default model.
window.gemEd=()=>document.querySelector('.ql-editor');
window.gemAttach=name=>{const f=benchFile(name);const dt=new DataTransfer();dt.items.add(f);const ed=gemEd();ed.focus();ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));benchClear();return name+' '+f.size;};
window.gemType=t=>{const ed=gemEd();ed.focus();document.execCommand('insertText',false,t);return ed.innerText.length;};
window.gemSendBtn=()=>document.querySelector('button[aria-label="Send message"],button.send-button');
window.gemBusy=()=>!!document.querySelector('button[aria-label*="Stop"]');
window.gemResponses=()=>[...document.querySelectorAll('model-response')];
window.gemTemp=()=>/Just stopping by/i.test(document.body.innerText);
window.gemTempBtn=()=>[...document.querySelectorAll('button')].find(b=>/Temporary chat/.test(b.getAttribute('aria-label')||''));
window.gemNew=async()=>{const a=[...document.querySelectorAll('a')].filter(e=>(e.getAttribute('aria-label')||'')==='New chat');a[a.length-1].click();await sleep(3000);if(!gemTemp()){const tb=gemTempBtn();if(tb)tb.click();await sleep(4000);}return JSON.stringify({url:location.pathname,temp:gemTemp(),ed:!!gemEd(),nResp:gemResponses().length});};
window.gemClickSend=async()=>{for(let i=0;i<40;i++){const s=gemSendBtn();if(s&&!s.disabled&&s.getAttribute('aria-disabled')!=='true'){s.click();return 'sent '+i;}await sleep(1500);}return 'timeout';};
window.gemStart=async(name,prompt)=>{window.T0=Date.now();if(name){gemAttach(name);await sleep(5000);}gemType(prompt);await sleep(1000);return await gemClickSend();};
window.gemAns=()=>{const r=gemResponses();const last=r.length?r[r.length-1].innerText:'';return JSON.stringify({nAns:r.length,secs:Math.round((Date.now()-T0)/1000)})+'\n'+compact(last);};
window.gemPoll=async(n,ms=30000)=>{const t0=Date.now();let last='',st=0;while(Date.now()-t0<ms){await sleep(2000);const r=gemResponses();const cur=r.length>=n?r[r.length-1].innerText:'';if(cur&&!gemBusy()&&cur===last&&cur.includes('}')){if(!st)st=Date.now();if(Date.now()-st>3000){window.LA=gemAns();return 'DONE '+Math.round((Date.now()-T0)/1000)+'s';}}else st=0;last=cur;}return 'pending';};
window.gemReset=()=>{window.STEP='t1';window.LA1='';window.LA2='';};
window.gemStep=async()=>{if(window.STEP==='complete')return 'COMPLETE';const r=await gemPoll(window.STEP==='t2'?2:1);if(r==='pending')return 'pending '+window.STEP;if(window.STEP!=='t2'){window.LA1=LA;window.STEP='t2';await gemStart(null,P2);return 't1 '+r+' -> sent t2';}window.LA2=LA;window.STEP='complete';return 'COMPLETE '+r;};
'gemini ok';
