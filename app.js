const $=id=>document.getElementById(id);let gigs=[];
const sets={
'Web Development':[
['I will build a modern responsive website','business website, responsive design, web development'],
['I will build a professional SaaS website','saas website, startup website, web development'],
['I will build a modern AI website','ai website, ai web app, modern website'],
['I will build a custom React website','react website, react js, frontend'],
['I will convert Figma to responsive HTML','figma to html, figma to website, responsive'],
['I will build a custom business dashboard','admin dashboard, web app, dashboard ui'],
['I will redesign your existing website','website redesign, ui ux, responsive'],
['I will fix HTML CSS JavaScript bugs','html css fix, javascript bug, website fix'],
['I will build a mobile first website','mobile website, responsive, frontend'],
['I will create a fast SEO friendly website','seo website, speed optimization, web development']
],
'AI Websites':[
['I will build a modern AI website','ai website, ai startup, ai web app'],
['I will create an AI SaaS landing page','ai saas, landing page, startup'],
['I will build an AI chatbot interface','ai chatbot, chatbot ui, ai assistant'],
['I will create an AI product website','ai product, responsive website, ai web design'],
['I will build an AI tools directory website','ai tools, directory website, ai web'],
['I will create a modern AI dashboard','ai dashboard, saas dashboard, web app'],
['I will integrate AI features into your website','ai integration, api integration, ai website'],
['I will build a responsive AI landing page','ai landing page, responsive, conversion'],
['I will create an AI startup MVP frontend','ai mvp, startup, react frontend'],
['I will redesign your AI website','ai website redesign, ui ux, web design']
],
'SaaS':[
['I will build a modern SaaS landing page','saas landing page, startup, saas website'],
['I will create a professional SaaS dashboard','saas dashboard, dashboard ui, web app'],
['I will build your SaaS MVP frontend','saas mvp, react, web app'],
['I will design a high converting pricing page','pricing page, saas, conversion'],
['I will create a complete responsive SaaS website','saas website, responsive, startup'],
['I will build a SaaS admin panel','admin panel, saas, dashboard'],
['I will create a SaaS onboarding flow','saas onboarding, ux, product design'],
['I will build a SaaS analytics dashboard','analytics dashboard, saas, charts'],
['I will redesign your SaaS website','saas redesign, ui ux, website'],
['I will build a clean SaaS waitlist page','waitlist page, saas, startup']
],
'Landing Pages':[
['I will build a high converting landing page','landing page, conversion, business website'],
['I will create a modern product landing page','product landing page, modern website, startup'],
['I will build a SaaS landing page with pricing and FAQ','saas landing page, pricing, faq'],
['I will create a mobile first landing page','mobile website, landing page, responsive'],
['I will redesign your landing page for better conversions','landing page redesign, conversion, ui'],
['I will build a lead generation landing page','lead generation, landing page, marketing'],
['I will create a startup launch landing page','startup landing page, launch, web design'],
['I will build a waitlist landing page','waitlist, landing page, startup'],
['I will create a webinar landing page','webinar landing page, lead generation, design'],
['I will build a professional service landing page','service landing page, business, responsive']
],
'Chrome Extensions':[
['I will build a custom Chrome extension','chrome extension, browser extension, javascript'],
['I will create a professional Chrome extension popup UI','chrome extension, popup ui, frontend'],
['I will turn your web idea into a Chrome extension','chrome extension, web app, browser tool'],
['I will fix bugs in your Chrome extension','chrome extension fix, javascript, debugging'],
['I will build a simple productivity Chrome extension','chrome extension, productivity, browser tool'],
['I will create a Chrome extension dashboard','chrome extension, dashboard, web app'],
['I will add API integration to your Chrome extension','chrome extension, api integration, javascript'],
['I will redesign your Chrome extension UI','chrome extension ui, redesign, frontend'],
['I will convert a website feature into a Chrome extension','chrome extension, website, browser'],
['I will build a Chrome extension MVP','chrome extension mvp, javascript, browser']
],
'API Integration':[
['I will integrate an API into your website or web app','api integration, javascript, web app'],
['I will build a custom API dashboard','api dashboard, frontend, web app'],
['I will connect your website to a third party API','api integration, api connection, website'],
['I will create a REST API frontend interface','rest api, frontend, javascript'],
['I will debug API integration errors in your app','api debugging, javascript, web development'],
['I will integrate payment APIs into your website','payment api, api integration, web development'],
['I will connect your app to a JSON API','json api, api connection, web app'],
['I will integrate an AI API into your app','ai api, api integration, ai web app'],
['I will build API documentation pages','api documentation, developer docs, web'],
['I will create a custom API testing dashboard','api testing, dashboard, developer tool']
],
'Android Apps':[
['I will convert your website into a modern Android app','android app, webview, mobile app'],
['I will build a simple Android app from your idea','android development, mobile app, apk'],
['I will create a responsive mobile app UI','mobile app ui, android, app design'],
['I will turn your web app into an installable PWA','pwa, web app, mobile'],
['I will fix issues in your Android app','android bug fix, mobile app, debugging'],
['I will build a modern Android dashboard','android dashboard, mobile ui, app'],
['I will create an Android app landing screen','android ui, app design, mobile'],
['I will connect your Android app to an API','android api, api integration, mobile app'],
['I will redesign your Android app UI','android redesign, ui ux, mobile'],
['I will build a simple Android business app','android app, business app, mobile development']
]};

function makeGigs(){
  const cat=$('category').value;
  const count=Math.min(20,Math.max(1,Number($('count').value)||20));
  const min=Math.max(5,Number($('minPrice').value)||25);
  const max=Math.max(min+10,Number($('maxPrice').value)||150);
  $('minPrice').value=min;$('maxPrice').value=max;$('count').value=count;
  const base=sets[cat];
  const suffixes=['fast delivery','premium quality','mobile friendly','clean code','modern UI'];
  gigs=Array.from({length:count},(_,i)=>{
    const [baseTitle,keywords]=base[i%base.length];
    const cycle=Math.floor(i/base.length);
    const title=cycle===0?baseTitle:`${baseTitle} — ${suffixes[cycle%suffixes.length]}`;
    const basic=Math.round(min+(max-min)*.2);
    const standard=Math.round(min+(max-min)*.55);
    const premium=Math.round(max-(max-min)*.05);
    return{id:i+1,title,keywords,description:`Professional ${cat.toLowerCase()} service with a clean, responsive and conversion-focused implementation.`,packages:{basic,standard,premium},delivery:['2 days','3 days','4 days'][i%3],revisions:[1,2,3][i%3]};
  });
  render();
}

function escapeHtml(v){return String(v).replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[m]));}

function render(){
  const box=$('results');
  $('status').textContent=gigs.length;
  if(!gigs.length){box.className='results empty';box.innerHTML='<p>Click <b>GENERATE GIGS</b> to create your list.</p>';return;}
  box.className='results';
  box.innerHTML=gigs.map(g=>`<article class="gig"><div class="gig-index">${g.id}</div><div class="gig-body"><p class="gig-title">${escapeHtml(g.title)}</p><div class="gig-meta">$${g.packages.basic} / $${g.packages.standard} / $${g.packages.premium} · ${g.delivery}</div></div><button class="copy" data-id="${g.id}">Copy</button></article>`).join('');
  document.querySelectorAll('.copy').forEach(b=>b.onclick=()=>{
    const g=gigs.find(x=>x.id==b.dataset.id);if(!g)return;
    navigator.clipboard.writeText(`${g.title}\n\n${g.description}\n\nBasic: $${g.packages.basic}\nStandard: $${g.packages.standard}\nPremium: $${g.packages.premium}\nDelivery: ${g.delivery}\nRevisions: ${g.revisions}\nKeywords: ${g.keywords}`);
    b.textContent='✓';setTimeout(()=>b.textContent='Copy',1200);
  });
}

$('generate').onclick=makeGigs;
$('clear').onclick=()=>{gigs=[];render();};
$('export').onclick=()=>{if(!gigs.length)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(gigs,null,2)],{type:'application/json'}));a.download='fiverr-gigs.json';a.click();URL.revokeObjectURL(a.href);};
makeGigs();
