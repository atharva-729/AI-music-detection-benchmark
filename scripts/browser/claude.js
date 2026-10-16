// Claude driver (load common.js first). Normal chat (incognito rejects MP3), Sonnet 5.5 Medium, memory off.
window.cldInput='#chat-input-file-upload-onpage';
window.cldSendBtn=()=>document.querySelector('[data-testid=chat-input-send]');
window.cldBusy=()=>!!document.querySelector('button[aria-label*="Stop"],[data-testid=stop-button]');
window.cldResponses=()=>[...document.querySelectorAll('[data-testid=assistant-message], .font-claude-response, .font-claude-message')].filter((e,i,a)=>!a.some(o=>o!==e&&o.contains(e)));
window.cldModel=()=>{const m=document.querySelector('[data-testid=model-selector-dropdown]');return m?m.innerText.trim():null;};
window.cldNew=async()=>{const a=[...document.querySelectorAll('a[href="/new"]')];if(a.length){a[0].click();}await sleep(3000);return JSON.stringify({url:location.pathname,model:cldModel(),pm:!!document.querySelector('.ProseMirror'),nResp:cldResponses().length});};
window.cldClickSend=async()=>{for(let i=0;i<40;i++){const s=cldSendBtn();if(s&&!s.disabled){s.click();return 'sent '+i;}await sleep(1500);}return 'timeout';};
window.cldStart=async(name,prompt)=>{window.T0=Date.now();if(name){await benchSend(name,cldInput);await sleep(4000);}benchPaste(prompt);await sleep(1000);return await cldClickSend();};
window.cldBody=t=>{const m=[...t.matchAll(/\n\s*\{/g)];return m.length?t.slice(m[m.length-1].index):t;}; // skip the truncated 'Claude responded:' summary
window.cldAns=()=>{const r=cldResponses();const last=r.length?r[r.length-1].innerText:'';return JSON.stringify({nAns:r.length,secs:Math.round((Date.now()-T0)/1000)})+'\n'+compact(cldBody(last));};
window.cldPoll=async(n,ms=30000)=>{const t0=Date.now();let last='',st=0;while(Date.now()-t0<ms){await sleep(2000);const r=cldResponses();const cur=r.length>=n?r[r.length-1].innerText:'';if(cur&&!cldBusy()&&cur===last&&cur.includes('}')){if(!st)st=Date.now();if(Date.now()-st>3000){window.LA=cldAns();return 'DONE '+Math.round((Date.now()-T0)/1000)+'s';}}else st=0;last=cur;}return 'pending';};
window.cldReset=()=>{window.STEP='t1';window.LA1='';window.LA2='';};
window.cldStep=async()=>{if(window.STEP==='complete')return 'COMPLETE';const r=await cldPoll(window.STEP==='t2'?2:1);if(r==='pending')return 'pending '+window.STEP;if(window.STEP!=='t2'){window.LA1=LA;window.STEP='t2';await cldStart(null,P2);return 't1 '+r+' -> sent t2';}window.LA2=LA;window.STEP='complete';return 'COMPLETE '+r;};
'claude ok';
