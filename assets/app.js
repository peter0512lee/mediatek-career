'use strict';
const layers = {
  NAS: ['NON-ACCESS STRATUM', 'NAS · 與核心網路對話', '處理註冊、移動性與 session 管理等控制程序。5G 中相關控制功能分布於 AMF、SMF 等核心網路功能。', '註冊進行到哪一步？是否收到拒絕與原因碼？'],
  RRC: ['RADIO RESOURCE CONTROL', 'RRC · 管理無線連線', '負責無線連線與資源的控制，例如連線建立、重設與釋放。RRC 是終端與 RAN 之間的控制協定。', '目前處於什麼連線狀態？設定是否完成？何時發生狀態變化？'],
  PDCP: ['PACKET DATA CONVERGENCE PROTOCOL', 'PDCP · 處理封包與安全', '依承載類型與設定，負責序號、重排序、安全處理等功能。使用者平面的 header compression 也屬於這一層的功能範圍。', '封包序號、重排序或安全設定是否異常？'],
  RLC: ['RADIO LINK CONTROL', 'RLC · 分段、重組與重傳', '處理資料分段與重組；在 acknowledged mode 下也提供 ARQ 重傳。不是每一種 RLC mode 都執行重傳。', '資料是否等待重組？是否有重傳或未完成的資料？'],
  MAC: ['MEDIUM ACCESS CONTROL', 'MAC · 分配與使用傳輸資源', '處理邏輯通道多工、優先權與 HARQ 等機制，與無線資源排程互動；排程控制主要位於基地台側。', '是否取得傳輸資源？HARQ 重傳是否頻繁？'],
  PHY: ['PHYSICAL LAYER', 'PHY · 把資料送上無線鏈路', '處理編碼、調變、實體訊號收發等底層工作。第一輪先知道它與無線訊號品質、同步和傳輸能力有關。', '訊號品質與同步是否正常？是否有實體層解碼失敗？']
};
const layerButtons = document.querySelectorAll('[data-layer]');
layerButtons.forEach(button => button.addEventListener('click', () => {
  layerButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  ['layer-full', 'layer-title', 'layer-desc', 'layer-example'].forEach((id, index) => {
    document.getElementById(id).textContent = layers[button.dataset.layer][index];
  });
}));
const terms = [...document.querySelectorAll('.term')];
document.getElementById('term-search')?.addEventListener('input', event => {
  const query = event.target.value.trim().toLocaleLowerCase();
  let count = 0;
  terms.forEach(term => {
    term.hidden = !term.textContent.toLocaleLowerCase().includes(query);
    if (!term.hidden) count++;
  });
  document.getElementById('search-status').textContent = query ? (count ? `找到 ${count} 個名詞` : '找不到符合的名詞，試試英文縮寫或其他關鍵字。') : '';
});
const completed = document.getElementById('completed');
const completionStatus = document.getElementById('completion-status');
const progressKey = `fieldnotes.${document.body.dataset.chapter || 'modem-foundations'}.completed`;
if (completed && completionStatus) {
function displayProgress() {
  completionStatus.textContent = completed.checked ? '已完成本篇 · 可繼續下一個主題' : '進度僅儲存在此瀏覽器';
}
try { completed.checked = localStorage.getItem(progressKey) === 'true'; } catch { /* Reading stays available without storage. */ }
displayProgress();
completed.addEventListener('change', () => {
  displayProgress();
  try { localStorage.setItem(progressKey, String(completed.checked)); }
  catch { completionStatus.textContent = '目前瀏覽器無法儲存進度；本次勾選仍有效。'; }
});
}
const links = [...document.querySelectorAll('nav a')];
function setActive(id) {
  links.forEach(link => {
    const active = link.hash === `#${id}`;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) setActive(entry.target.id); });
  }, { rootMargin: '-10% 0px -60% 0px' });
  document.querySelectorAll('main section').forEach(section => observer.observe(section));
}
setActive(location.hash.slice(1) || document.querySelector('main section')?.id);
links.forEach(link => link.addEventListener('click', () => setActive(link.hash.slice(1))));
