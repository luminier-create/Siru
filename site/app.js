/* 시루 SIRU — 인터랙션 */
(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const CFG = JSON.parse($('#cfg').textContent);
  const mqReduce = matchMedia('(prefers-reduced-motion: reduce)');
  const reduced = () => mqReduce.matches;
  const SPRING = getComputedStyle(root).getPropertyValue('--spring').trim() || 'cubic-bezier(.34,1.56,.64,1)';
  const SPRING_SOFT = getComputedStyle(root).getPropertyValue('--spring-soft').trim() || 'cubic-bezier(.22,1.12,.36,1)';
  const OUT = 'cubic-bezier(.16,1,.3,1)';
  const buzz = (p = 8) => { try { navigator.vibrate && navigator.vibrate(p); } catch (e) { /* noop */ } };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* noop */ } },
  };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const wait = (ms) => new Promise((r) => setTimeout(r, reduced() ? 0 : ms));
  const pad = (n) => String(n).padStart(2, '0');

  /* ------------------------------------------------------------ 토스트 */
  const toastEl = $('#toast');
  let toastT;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove('show'), 1900);
  }

  /* ------------------------------------------------------------ 테마 (원형 전환) */
  const themeBtn = $('#themeBtn');
  const tc = $('#tc');
  function applyTheme(t, persist) {
    root.dataset.theme = t;
    if (persist) store.set('siru-theme', t);
    themeBtn.setAttribute('aria-label', t === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
    if (tc) tc.content = t === 'dark' ? CFG.themeDark : CFG.themeLight;
  }
  applyTheme(root.dataset.theme || 'light', false);
  themeBtn.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    buzz(6);
    if (!document.startViewTransition || reduced()) return applyTheme(next, true);
    const r = themeBtn.getBoundingClientRect();
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    const rad = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    root.classList.add('vt-theme');
    const vt = document.startViewTransition(() => applyTheme(next, true));
    vt.ready.then(() => {
      root.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${rad}px at ${x}px ${y}px)`] },
        { duration: 700, easing: OUT, pseudoElement: '::view-transition-new(root)' },
      );
    });
    vt.finished.finally(() => root.classList.remove('vt-theme'));
  });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!store.get('siru-theme')) applyTheme(e.matches ? 'dark' : 'light', false);
  });

  /* ------------------------------------------------------------ 상단바 숨김 */
  const topbar = $('#topbar');
  let lastY = scrollY, ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      if (y < 140 || y < lastY - 6) {
        topbar.classList.remove('is-hidden');
        document.body.classList.remove('top-hidden');
      } else if (y > lastY + 6) {
        topbar.classList.add('is-hidden');
        document.body.classList.add('top-hidden');
      }
      lastY = y;
      ticking = false;
    });
  }, { passive: true });

  /* ------------------------------------------------------------ 스크롤 스파이 */
  const navLinks = $$('.top-links a, .tabbar a');
  const tabbar = $('.tabbar');
  const tabs = tabbar ? $$('a', tabbar) : [];
  function setActive(id) {
    navLinks.forEach((a) => {
      if (a.getAttribute('href') === '#' + id) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
    if (!tabbar) return;
    const i = tabs.findIndex((a) => a.getAttribute('href') === '#' + id);
    tabbar.style.setProperty('--i', Math.max(0, i));
    tabbar.style.setProperty('--on', i >= 0 ? 1 : 0);
  }
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) setActive(e.target.id); });
  }, { rootMargin: '-45% 0px -50% 0px' });
  new Set(navLinks.map((a) => a.getAttribute('href').slice(1))).forEach((id) => {
    const s = document.getElementById(id);
    if (s) spy.observe(s);
  });
  spy.observe($('#top'));

  /* ------------------------------------------------------------ 등장 · 카운트업 */
  function countUp(el) {
    const end = +el.dataset.count;
    if (reduced()) { el.textContent = end; return; }
    const t0 = performance.now(), dur = 1500;
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 4)));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      $$('[data-count]', e.target).forEach(countUp);
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });
  $$('.reveal, .sec-head .squiggle').forEach((el) => io.observe(el));

  /* ------------------------------------------------------------ 히어로: 쫀득한 떡 */
  const stage = $('#stage');
  const mochi = $('#mochi');
  const inner = $('.mochi-inner', mochi);
  const bubble = $('#bubble');
  const hint = $('#hint');
  let taps = 0, bubbleT;

  function say(text, secret) {
    bubble.textContent = text;
    bubble.classList.toggle('secret', !!secret);
    bubble.classList.remove('show');
    void bubble.offsetWidth;
    bubble.classList.add('show');
    clearTimeout(bubbleT);
    bubbleT = setTimeout(() => bubble.classList.remove('show'), secret ? 3200 : 1800);
  }

  // 팥알 · 하트 파티클
  function burst(host, n, big) {
    if (reduced()) return;
    const beans = ['#8C2F2B', '#A8433A', '#6E2622', '#B85A4E'];
    for (let i = 0; i < n; i++) {
      const p = document.createElement('span');
      const heart = i % (big ? 3 : 4) === 0;
      p.className = 'particle' + (heart ? ' heart' : '');
      if (heart) {
        p.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><use href="#i-heart"/></svg>';
      } else {
        const w = 10 + Math.random() * 8;
        p.style.setProperty('--c', beans[i % beans.length]);
        p.style.setProperty('--w', w + 'px');
        p.style.setProperty('--h', w * 0.72 + 'px');
      }
      host.appendChild(p);
      const a = Math.random() * Math.PI * 2;
      const d = (big ? 140 : 90) + Math.random() * (big ? 130 : 70);
      const dx = Math.cos(a) * d, dy = Math.sin(a) * d - 50;
      const rot = Math.random() * 540 - 270;
      p.animate([
        { transform: 'translate(-50%,-50%) scale(.2)', opacity: 1 },
        { transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px)) scale(1) rotate(${rot * 0.6}deg)`, opacity: 1, offset: 0.62 },
        { transform: `translate(calc(-50% + ${dx * 1.12}px), calc(-50% + ${dy + 70}px)) scale(.7) rotate(${rot}deg)`, opacity: 0 },
      ], { duration: 950 + Math.random() * 550, easing: OUT }).onfinish = () => p.remove();
    }
  }

  mochi.addEventListener('click', () => {
    taps++;
    buzz(12);
    hint && hint.classList.add('gone');
    inner.animate([
      { transform: 'scale(1,1)' },
      { transform: 'scale(1.24,.76)', offset: 0.14 },
      { transform: 'scale(.86,1.16)', offset: 0.34 },
      { transform: 'scale(1.08,.93)', offset: 0.54 },
      { transform: 'scale(.97,1.03)', offset: 0.76 },
      { transform: 'scale(1,1)' },
    ], { duration: reduced() ? 1 : 950, easing: 'ease-out' });
    const secret = taps % CFG.secretAfter === 0;
    say(secret ? CFG.secret : CFG.lines[(taps - 1) % CFG.lines.length], secret);
    burst(stage, secret ? 26 : 10, secret);
    if (secret) buzz([10, 40, 10, 40, 30]);
  });

  // 포인터 패럴랙스 (마우스 환경)
  if (matchMedia('(pointer: fine)').matches) {
    const hero = $('#top');
    let raf = 0, px = 0, py = 0;
    const paint = () => {
      stage.style.setProperty('--px', (px * -26).toFixed(1));
      stage.style.setProperty('--py', (py * -26).toFixed(1));
      mochi.style.setProperty('--tx', (px * 16).toFixed(1));
      mochi.style.setProperty('--ty', (py * 16).toFixed(1));
      raf = 0;
    };
    hero.addEventListener('pointermove', (e) => {
      if (reduced()) return;
      const r = hero.getBoundingClientRect();
      px = (e.clientX - r.left) / r.width - 0.5;
      py = (e.clientY - r.top) / r.height - 0.5;
      if (!raf) raf = requestAnimationFrame(paint);
    });
    hero.addEventListener('pointerleave', () => { px = py = 0; if (!raf) raf = requestAnimationFrame(paint); });
  }

  /* ------------------------------------------------------------ 채팅 데모 */
  const thread = $('#thread');
  const replay = $('#replay');
  const chat = JSON.parse($('#chat-data').textContent);
  let chatRun = 0;
  const node = (cls, html) => { const d = document.createElement('div'); d.className = cls; d.innerHTML = html; return d; };
  function trim() { while (thread.children.length > 8) thread.firstElementChild.remove(); }
  async function playChat() {
    const run = ++chatRun;
    thread.innerHTML = '';
    replay.hidden = true;
    chat.forEach((m) => { if (m.src) { const im = new Image(); im.src = m.src; } });
    for (const m of chat) {
      if (run !== chatRun) return;
      if (m.from === 'friend') {
        const t = node('typing', '<i></i><i></i><i></i>');
        thread.append(t); trim();
        await wait(950);
        t.remove();
      } else {
        await wait(520);
      }
      if (run !== chatRun) return;
      thread.append(m.text
        ? node(`msg ${m.from} text`, esc(m.text))
        : node(`msg ${m.from} stk`, `<img src="${esc(m.src)}" alt="" width="360" height="360">`));
      trim();
      await wait(m.text ? 650 : 1050);
    }
    replay.hidden = false;
  }
  new IntersectionObserver(([e], obs) => {
    if (e.isIntersecting) { playChat(); obs.disconnect(); }
  }, { threshold: 0.45 }).observe($('.phone'));
  replay.addEventListener('click', () => { buzz(); playChat(); });

  /* ------------------------------------------------------------ 신분증 뒤집기 */
  const idcard = $('#idcard');
  const idToggle = $('#idToggle');
  const idHint = $('#idHint');
  idToggle.addEventListener('click', () => {
    const on = idcard.classList.toggle('flipped');
    idToggle.setAttribute('aria-pressed', String(on));
    idHint.textContent = on ? CFG.idBack : CFG.idFront;
    buzz(on ? [8, 30, 14] : 8);
  });

  /* ------------------------------------------------------------ 갤러리 */
  const grid = $('#grid');
  const items = $$('.card', grid).map((li, i) => ({
    li, i,
    a: $('a', li),
    img: $('img', li),
    title: li.dataset.title,
    sub: li.dataset.sub,
    cat: li.dataset.cat,
    catLabel: li.dataset.catLabel,
    src: $('a', li).getAttribute('href'),
  }));
  const chips = $$('.chip');
  const q = $('#q');
  const qClear = $('#qClear');
  const countEl = $('#galCount');
  const empty = $('#empty');
  let filter = 'all', query = '';

  items.forEach(({ img }) => {
    if (img.complete && img.naturalWidth) img.classList.add('ok');
    else img.addEventListener('load', () => img.classList.add('ok'), { once: true });
  });

  const norm = (s) => (s || '').toLowerCase().replace(/\s+/g, '');
  const visible = () => items.filter((it) => !it.li.hidden);

  function applyFilter(animate = true) {
    const nq = norm(query);
    const run = () => {
      let n = 0;
      items.forEach((it) => {
        const ok = (filter === 'all' || it.cat === filter) && (!nq || norm(it.title + ' ' + it.sub + ' ' + it.catLabel).includes(nq));
        it.li.hidden = !ok;
        if (ok) n++;
      });
      countEl.textContent = n;
      empty.hidden = n > 0;
    };
    if (animate && document.startViewTransition && !reduced()) {
      items.forEach((it) => { it.li.style.viewTransitionName = 'c' + it.i; });
      const vt = document.startViewTransition(run);
      vt.finished.finally(() => items.forEach((it) => { it.li.style.viewTransitionName = ''; }));
    } else {
      run();
    }
  }

  function keepGridInView() {
    const r = grid.getBoundingClientRect();
    if (r.top < 0) scrollTo({ top: scrollY + r.top - 170, behavior: reduced() ? 'auto' : 'smooth' });
  }

  chips.forEach((c) => c.addEventListener('click', () => {
    if (c.getAttribute('aria-pressed') === 'true') return;
    chips.forEach((x) => x.setAttribute('aria-pressed', String(x === c)));
    filter = c.dataset.f;
    buzz(5);
    applyFilter();
    keepGridInView();
    c.scrollIntoView({ inline: 'center', block: 'nearest', behavior: reduced() ? 'auto' : 'smooth' });
  }));

  let qT;
  q.addEventListener('input', () => {
    qClear.hidden = !q.value;
    clearTimeout(qT);
    qT = setTimeout(() => { query = q.value.trim(); applyFilter(); }, 140);
  });
  qClear.addEventListener('click', () => {
    q.value = ''; qClear.hidden = true; query = ''; applyFilter(); q.focus();
  });
  q.addEventListener('keydown', (e) => { if (e.key === 'Enter') q.blur(); });

  /* ------------------------------------------------------------ 뷰어 */
  const dlg = $('#viewer');
  const vShell = $('.v-shell', dlg);
  const vStage = $('#vStage');
  const vCard = $('#vCard');
  const vImg = $('#vImg');
  const vTitle = $('#vTitle');
  const vSub = $('#vSub');
  const vCat = $('#vCat');
  const vCount = $('#vCount');
  const vSave = $('#vSave');
  const vShare = $('#vShare');
  const vRibbon = $('#vRibbon');
  const vActions = $('.v-actions', dlg);
  let list = items, cur = 0, pushed = false, busy = false;
  const blobs = new Map();

  function preload(i) {
    const it = list[(i + list.length) % list.length];
    if (!it) return;
    const im = new Image(); im.src = it.src;
  }
  function prefetchBlob(it) {
    if (blobs.has(it.src) || !('canShare' in navigator)) return;
    blobs.set(it.src, null);
    fetch(it.src).then((r) => r.blob()).then((b) => blobs.set(it.src, b)).catch(() => blobs.delete(it.src));
  }
  function render() {
    const it = list[cur];
    vImg.src = it.src;
    vImg.alt = `시루 이모티콘 — ${it.title}`;
    vTitle.textContent = it.title;
    vSub.textContent = it.sub;
    vCat.textContent = it.catLabel;
    vCount.textContent = `${pad(cur + 1)} / ${pad(list.length)}`;
    vSave.href = it.src;
    vSave.setAttribute('download', `siru-${it.title.replace(/[\\/:*?"<>|\s]+/g, '_')}.png`);
    preload(cur + 1); preload(cur - 1);
    prefetchBlob(it);
  }
  const hashFor = (it) => '#e=' + encodeURIComponent(it.title);

  function rotOf(li) {
    const r = parseFloat(getComputedStyle(li.firstElementChild).rotate);
    return isNaN(r) ? 0 : r;
  }
  function flip(fromEl, reverse) {
    const target = fromEl && fromEl.getBoundingClientRect();
    if (!target || !target.width || reduced()) {
      return vCard.animate(
        reverse ? [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(.88)' }]
          : [{ opacity: 0, transform: 'scale(.9)' }, { opacity: 1, transform: 'none' }],
        { duration: reduced() ? 1 : 320, easing: OUT, fill: 'forwards' },
      );
    }
    const b = vCard.getBoundingClientRect();
    const s = target.width / b.width;
    const dx = target.left + target.width / 2 - (b.left + b.width / 2);
    const dy = target.top + target.height / 2 - (b.top + b.height / 2);
    const from = { transform: `translate(${dx}px, ${dy}px) scale(${s}) rotate(${rotOf(fromEl.closest('li') || fromEl)}deg)`, borderRadius: '44px' };
    const to = { transform: 'none', borderRadius: '34px' };
    return vCard.animate(reverse ? [to, from] : [from, to], {
      duration: reverse ? 420 : 760, easing: reverse ? OUT : SPRING_SOFT, fill: reverse ? 'forwards' : 'none',
    });
  }

  function openViewer(idx, fromEl, opts = {}) {
    list = opts.all ? items : visible();
    if (!list.length) list = items;
    cur = Math.max(0, list.indexOf(items[idx]));
    vRibbon.hidden = true;
    render();
    if (!dlg.open) {
      dlg.classList.remove('closing');
      dlg.style.removeProperty('--fade');
      dlg.showModal();
      root.classList.add('modal-open');
      tabbar && tabbar.classList.add('is-away');
      if (!opts.fromHash) {
        history.pushState({ viewer: 1 }, '', hashFor(list[cur]));
        pushed = true;
      }
      flip(fromEl);
    } else {
      history.replaceState(history.state, '', hashFor(list[cur]));
    }
  }

  function doClose() {
    if (!dlg.open || dlg.classList.contains('closing')) return;
    const it = list[cur];
    const thumb = it && !it.li.hidden ? $('.pic', it.li) : null;
    const inView = thumb && (() => { const r = thumb.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; })();
    dlg.classList.add('closing');
    const anim = flip(inView ? thumb : null, true);
    const finish = () => {
      dlg.close();
      dlg.classList.remove('closing');
      vCard.getAnimations().forEach((a) => a.cancel());
      vCard.style.transform = '';
      root.classList.remove('modal-open');
      tabbar && tabbar.classList.remove('is-away');
      if (it && it.a) it.a.focus({ preventScroll: true });
    };
    anim.onfinish = finish;
    anim.oncancel = finish;
  }
  function closeViewer() {
    if (pushed && history.state && history.state.viewer) {
      history.back(); // popstate → doClose
    } else {
      doClose();
      history.replaceState(null, '', location.pathname + location.search);
    }
    pushed = false;
  }
  addEventListener('popstate', () => { if (dlg.open) { pushed = false; doClose(); } });

  function step(dir) {
    cur = (cur + dir + list.length) % list.length;
    vRibbon.hidden = true;
    render();
    history.replaceState(history.state, '', hashFor(list[cur]));
  }
  function swipeTo(dir, fromTransform) {
    if (busy) return;
    busy = true;
    buzz(5);
    const w = Math.min(innerWidth, 900);
    const out = vCard.animate(
      [{ transform: fromTransform || 'none' }, { transform: `translateX(${-dir * w}px) rotate(${-dir * 14}deg)`, opacity: 0.4 }],
      { duration: reduced() ? 1 : 200, easing: 'cubic-bezier(.5,0,.9,.4)', fill: 'forwards' },
    );
    out.onfinish = () => {
      step(dir);
      vCard.style.transform = '';
      out.cancel();
      vCard.animate(
        [{ transform: `translateX(${dir * w * 0.55}px) rotate(${dir * 9}deg)`, opacity: 0 }, { transform: 'none', opacity: 1 }],
        { duration: reduced() ? 1 : 720, easing: SPRING_SOFT },
      );
      busy = false;
    };
  }

  // 카드 클릭 → 뷰어 (JS 없으면 이미지 링크로 동작)
  grid.addEventListener('click', (e) => {
    const a = e.target.closest('.card a');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    const it = items.find((x) => x.a === a);
    buzz(6);
    openViewer(it.i, $('.pic', it.li));
  });

  $('#vClose').addEventListener('click', closeViewer);
  $('#vPrev').addEventListener('click', () => swipeTo(-1));
  $('#vNext').addEventListener('click', () => swipeTo(1));
  dlg.addEventListener('cancel', (e) => { e.preventDefault(); closeViewer(); });
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); swipeTo(1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); swipeTo(-1); }
  });
  vShell.addEventListener('click', (e) => { if (e.target === vShell) closeViewer(); });

  // 스와이프 제스처: 좌우 넘김, 아래로 닫기
  let sx = 0, sy = 0, dx = 0, dy = 0, t0 = 0, drag = false, axis = null;
  vStage.addEventListener('pointerdown', (e) => {
    if (e.button || busy) return;
    drag = true; axis = null; dx = dy = 0;
    sx = e.clientX; sy = e.clientY; t0 = performance.now();
    vStage.setPointerCapture(e.pointerId);
    vCard.getAnimations().forEach((a) => a.finish());
  });
  vStage.addEventListener('pointermove', (e) => {
    if (!drag) return;
    dx = e.clientX - sx; dy = e.clientY - sy;
    if (!axis && Math.hypot(dx, dy) > 8) axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
    if (axis === 'x') {
      vCard.style.transform = `translateX(${dx}px) rotate(${dx / 20}deg)`;
    } else if (axis === 'y') {
      const d = Math.max(0, dy);
      vCard.style.transform = `translateY(${d}px) scale(${1 - d / 1400})`;
      dlg.style.setProperty('--fade', String(1 - Math.min(d / 420, 0.75)));
    }
  });
  const endDrag = (e) => {
    if (!drag) return;
    drag = false;
    const dt = Math.max(1, performance.now() - t0);
    const tf = vCard.style.transform;
    if (axis === 'x' && (Math.abs(dx) > 80 || Math.abs(dx / dt) > 0.5)) {
      swipeTo(dx < 0 ? 1 : -1, tf);
    } else if (axis === 'y' && (dy > 110 || dy / dt > 0.6)) {
      closeViewer();
    } else {
      if (tf) {
        vCard.style.transform = '';
        vCard.animate([{ transform: tf }, { transform: 'none' }], { duration: 600, easing: SPRING });
      }
      dlg.style.removeProperty('--fade');
      if (!axis && e.type === 'pointerup' && e.target === vStage) closeViewer();
    }
  };
  vStage.addEventListener('pointerup', endDrag);
  vStage.addEventListener('pointercancel', endDrag);

  // 공유: 이미지 파일 공유 → 링크 공유 → 링크 복사
  vShare.addEventListener('click', async () => {
    const it = list[cur];
    const url = location.origin + location.pathname + hashFor(it);
    const title = `${it.title} — 시루 SIRU`;
    buzz(6);
    try {
      const blob = blobs.get(it.src);
      if (blob && navigator.canShare) {
        const file = new File([blob], `siru-${it.title}.png`, { type: blob.type || 'image/png' });
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title, text: `${it.title} · ${it.sub}\n${url}` });
          return;
        }
      }
      if (navigator.share) { await navigator.share({ title, text: `${it.title} · ${it.sub}`, url }); return; }
      await navigator.clipboard.writeText(url);
      toast(CFG.linkCopied);
    } catch (err) {
      if (err && err.name === 'AbortError') return;
      try { await navigator.clipboard.writeText(url); toast(CFG.linkCopied); } catch (_) { toast(url); }
    }
  });

  // 오늘의 표정 뽑기
  $('#gacha').addEventListener('click', async () => {
    if (busy) return;
    buzz(8);
    const pool = items;
    const pick = pool[Math.floor(Math.random() * pool.length)];
    const seq = Array.from({ length: 14 }, () => pool[Math.floor(Math.random() * pool.length)]).concat(pick);
    await Promise.race([
      Promise.all(seq.map((it) => new Promise((r) => { const im = new Image(); im.onload = im.onerror = r; im.src = it.src; }))),
      new Promise((r) => setTimeout(r, 900)),
    ]);
    openViewer(seq[0].i, null, { all: true });
    busy = true;
    vActions.style.pointerEvents = 'none';
    if (!reduced()) {
      for (let k = 1; k < seq.length; k++) {
        await new Promise((r) => setTimeout(r, 45 + k * k * 1.6));
        if (!dlg.open) { busy = false; vActions.style.pointerEvents = ''; return; }
        cur = items.indexOf(seq[k]);
        render();
        vCard.animate([{ transform: 'scale(.94) rotate(-2deg)' }, { transform: 'none' }], { duration: 160, easing: OUT });
        if (k % 3 === 0) buzz(3);
      }
    } else {
      cur = items.indexOf(pick); render();
    }
    history.replaceState(history.state, '', hashFor(pick));
    vRibbon.hidden = false;
    vRibbon.animate([{ transform: 'scale(0) rotate(-30deg)' }, { transform: 'scale(1) rotate(-8deg)' }], { duration: 700, easing: SPRING });
    vCard.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.08)' }, { transform: 'scale(1)' }], { duration: 700, easing: SPRING });
    burst(vStage, 24, true);
    buzz([12, 50, 20]);
    vActions.style.pointerEvents = '';
    busy = false;
  });

  // 딥 링크 (#e=표정이름)
  function fromHash() {
    const m = location.hash.match(/^#e=(.+)$/);
    if (!m) return;
    let t;
    try { t = decodeURIComponent(m[1]); } catch (e) { return; }
    const it = items.find((x) => x.title === t);
    if (!it) return;
    if (!dlg.open) openViewer(it.i, null, { fromHash: true, all: true });
  }
  addEventListener('hashchange', fromHash);
  fromHash();

  /* ------------------------------------------------------------ 이메일 복사 */
  const copyBtn = $('#copyEmail');
  copyBtn.addEventListener('click', async () => {
    const email = copyBtn.dataset.email;
    const label = $('span', copyBtn);
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(email);
      } else {
        const t = document.createElement('textarea');
        t.value = email; t.style.position = 'fixed'; t.style.opacity = '0';
        document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove();
      }
      copyBtn.classList.add('done');
      label.textContent = CFG.copiedShort;
      toast(CFG.copied);
      buzz([6, 30, 6]);
      setTimeout(() => { copyBtn.classList.remove('done'); label.textContent = CFG.copy; }, 1800);
    } catch (e) {
      window.prompt(CFG.copyPrompt, email);
    }
  });

  /* ------------------------------------------------------------ 오프라인 지원 */
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
  }
})();
