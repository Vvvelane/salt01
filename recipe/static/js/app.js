import { renderMarket } from './views/market.js';
import { renderDataAtlas } from './views/data_atlas.js';
import { renderResearch } from './views/research.js';

const routes = [['#/market','市场路径'],['#/data','数据语义'],['#/research','研究审计']];
const root = document.querySelector('#app');
async function route(){ const key=location.hash.split('?')[0]||'#/market'; root.innerHTML=`<div class="shell"><header><h1>Recipe</h1><p class="muted">只读量化研究数据浏览工具</p></header><nav class="nav" aria-label="主导航">${routes.map(([r,l])=>`<a href="${r}" class="${r===key?'active':''}">${l}</a>`).join('')}</nav><main id="view"></main></div>`; if(key==='#/data') await renderDataAtlas(document.querySelector('#view')); else if(key==='#/research') await renderResearch(document.querySelector('#view')); else await renderMarket(document.querySelector('#view')); }
addEventListener('hashchange',route); route();
