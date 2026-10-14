// ==========================================================================
// STARS DROP — Application Logic & Animations
// ==========================================================================

const tg = window.Telegram ? window.Telegram.WebApp : null;

// Application State
let state = {
    user: {
        id: 5721221489,
        first_name: "IBROHIM",
        username: "@IBROHIMBOI_UC",
        photo_url: "https://img.icons8.com/color/96/avatar.png",
        balance: 0,
        stars_balance: 25,
        completed_orders: 0,
        reg_date: "26.07.2026",
        inventory_count: 0
    },
    cases: [],
    packages: [],
    inventory: [],
    liveDrops: [],
    history: {
        orders: [],
        deposits: []
    },
    activeCase: null,
    currentWonItem: null,
    isSpinning: false,
    soundEnabled: true,
    fastSpin: false,
    settings: {
        cardNumber: "9860 6004 0697 7147",
        cardOwner: "XUJAMURATOVA ZARGUL",
        newsLink: "https://t.me/YAKUDZA_UC_NEWS",
        supportLink: "https://t.me/yakfast_support"
    }
};

// Web Audio API Synthesizer for Realistic Sound Effects
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function playTickSound() {
    if (!state.soundEnabled) return;
    try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(750, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 0.025);
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.025);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.025);
    } catch (e) {}
}

function playWinFanfare() {
    if (!state.soundEnabled) return;
    try {
        const ctx = getAudioContext();
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 arpeggio
        notes.forEach((freq, idx) => {
            setTimeout(() => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, ctx.currentTime);
                gain.gain.setValueAtTime(0.25, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.35);
            }, idx * 90);
        });
    } catch (e) {}
}

function triggerHaptic(type = 'light') {
    if (tg && tg.HapticFeedback) {
        if (type === 'success') {
            tg.HapticFeedback.notificationOccurred('success');
        } else if (type === 'medium') {
            tg.HapticFeedback.impactOccurred('medium');
        } else {
            tg.HapticFeedback.impactOccurred('light');
        }
    }
}

function toggleSound() {
    state.soundEnabled = !state.soundEnabled;
    const btn = document.getElementById("sound-toggle-btn");
    if (btn) btn.textContent = state.soundEnabled ? "🔊" : "🔇";
    showToast(state.soundEnabled ? "Ovoz yoqildi 🔊" : "Ovoz o'chirildi 🔇");
}

// DOM Cache
const els = {};

document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) window.lucide.createIcons();

    // Cache elements
    els.userAvatar = document.getElementById("user-avatar");
    els.profileAvatar = document.getElementById("profile-avatar");
    els.userDisplayName = document.getElementById("user-display-name");
    els.profileName = document.getElementById("profile-name");
    els.profileUsername = document.getElementById("profile-username");
    els.profileId = document.getElementById("profile-id");

    els.headerStars = document.getElementById("header-stars-amount");
    els.profileStars = document.getElementById("profile-stars-amount");
    els.profileUzs = document.getElementById("profile-uzs-amount");
    els.profileInvCount = document.getElementById("profile-inv-count");

    els.casesGrid = document.getElementById("cases-grid");
    els.liveDropsTrack = document.getElementById("live-drops-track");
    els.starsCatalog = document.getElementById("stars-catalog");
    els.premiumCatalog = document.getElementById("premium-catalog");

    els.cardNumber = document.getElementById("card-number");
    els.cardOwner = document.getElementById("card-owner");
    els.linkNews = document.getElementById("link-news");
    els.linkSupport = document.getElementById("link-support");
    els.toast = document.getElementById("toast");

    // Init Telegram User Data
    initTelegramData();

    // Load API Data
    fetchUserData();
    fetchCases();
    fetchLiveDrops();
    fetchCatalog();
    fetchInventory();

    // Init Wheel of Fortune Canvas
    initWheelCanvas();

    // Polling live drops
    setInterval(fetchLiveDrops, 8000);
});

// 1. Telegram WebApp Data
function initTelegramData() {
    if (!tg) return;
    tg.ready();
    tg.expand();

    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        const u = tg.initDataUnsafe.user;
        state.user.id = u.id;
        state.user.first_name = u.first_name || "Foydalanuvchi";
        state.user.username = u.username ? `@${u.username}` : "";
        state.user.photo_url = u.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(state.user.first_name)}&background=1e293b&color=ffffff&size=128`;
    }
}

// 2. Navigation Tabs
function switchTab(tabId) {
    triggerHaptic('light');

    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".nav-tab-btn").forEach(el => el.classList.remove("active"));

    const tabEl = document.getElementById(`tab-${tabId}`);
    if (tabEl) tabEl.classList.add("active");

    const tabsMap = ['cases', 'minigames', 'leaderboard', 'profile'];
    const idx = tabsMap.indexOf(tabId);
    if (idx !== -1) {
        document.querySelectorAll(".nav-tab-btn")[idx].classList.add("active");
    }

    if (tabId === 'profile') {
        fetchUserData();
        fetchInventory();
        fetchHistory();
    } else if (tabId === 'cases') {
        fetchCases();
    }
}

function switchProfileSection(secId) {
    triggerHaptic('light');
    document.querySelectorAll(".pst-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".profile-sub-content").forEach(s => s.classList.remove("active"));

    const btns = document.querySelectorAll(".profile-sub-tabs .pst-btn");
    if (secId === 'inventory') btns[0].classList.add("active");
    if (secId === 'deposit') btns[1].classList.add("active");
    if (secId === 'history') btns[2].classList.add("active");

    const secEl = document.getElementById(`psec-${secId}`);
    if (secEl) secEl.classList.add("active");

    if (secId === 'inventory') fetchInventory();
    if (secId === 'history') fetchHistory();
}

function scrollToCase(caseId) {
    switchTab('cases');
    setTimeout(() => {
        const el = document.getElementById(`card-${caseId}`);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.style.boxShadow = "0 0 25px rgba(245, 158, 11, 0.8)";
            setTimeout(() => { el.style.boxShadow = ""; }, 1500);
        }
    }, 150);
}

// 3. UI Render Profile & Balances
function renderProfile() {
    if (els.userAvatar) els.userAvatar.src = state.user.photo_url;
    if (els.profileAvatar) els.profileAvatar.src = state.user.photo_url;
    if (els.userDisplayName) els.userDisplayName.textContent = state.user.first_name;
    if (els.profileName) els.profileName.textContent = state.user.first_name;
    if (els.profileUsername) els.profileUsername.textContent = state.user.username || `ID: ${state.user.id}`;
    if (els.profileId) els.profileId.textContent = `ID: ${state.user.id}`;

    updateBalancesUI();

    if (els.cardNumber) els.cardNumber.textContent = state.settings.cardNumber;
    if (els.cardOwner) els.cardOwner.textContent = state.settings.cardOwner;
    if (els.linkNews) els.linkNews.href = state.settings.newsLink;
    if (els.linkSupport) els.linkSupport.href = state.settings.supportLink;
}

function updateBalancesUI() {
    const stars = Math.floor(state.user.stars_balance || 0);
    const uzs = `${(state.user.balance || 0).toLocaleString('uz-UZ')} UZS`;

    if (els.headerStars) els.headerStars.textContent = stars;
    if (els.profileStars) els.profileStars.textContent = stars;
    if (els.profileUzs) els.profileUzs.textContent = uzs;
    if (els.profileInvCount) els.profileInvCount.textContent = state.inventory.length;

    const convertBal = document.getElementById("convert-user-balance");
    if (convertBal) convertBal.textContent = uzs;
}

// 4. API Requests
async function fetchUserData() {
    try {
        const res = await fetch(`/api/user?user_id=${state.user.id}`);
        if (res.ok) {
            const data = await res.json();
            state.user.balance = data.balance || 0;
            state.user.stars_balance = data.stars_balance !== undefined ? data.stars_balance : 25;
            state.user.completed_orders = data.completed_orders || 0;
            if (data.settings) {
                state.settings.cardNumber = data.settings.card_number || state.settings.cardNumber;
                state.settings.cardOwner = data.settings.card_owner || state.settings.cardOwner;
                state.settings.newsLink = data.settings.news_link || state.settings.newsLink;
                state.settings.supportLink = data.settings.support_link || state.settings.supportLink;
            }
            renderProfile();
        }
    } catch (e) {
        console.error("fetchUserData error:", e);
    }
}

async function fetchCases() {
    try {
        const res = await fetch('/api/cases');
        if (res.ok) {
            state.cases = await res.json();
            renderCasesGrid();
        }
    } catch (e) {
        console.error("fetchCases error:", e);
    }
}

async function fetchLiveDrops() {
    try {
        const res = await fetch('/api/live_drops');
        if (res.ok) {
            state.liveDrops = await res.json();
            renderLiveDrops();
        }
    } catch (e) {
        console.error("fetchLiveDrops error:", e);
    }
}

async function fetchInventory() {
    try {
        const res = await fetch(`/api/inventory?user_id=${state.user.id}`);
        if (res.ok) {
            state.inventory = await res.json();
            renderInventory();
            updateBalancesUI();
        }
    } catch (e) {
        console.error("fetchInventory error:", e);
    }
}

async function fetchCatalog() {
    try {
        const res = await fetch('/api/packages');
        if (res.ok) {
            state.packages = await res.json();
            renderCatalog();
        }
    } catch (e) {
        console.error("fetchCatalog error:", e);
    }
}

// 5. Render Functions
function renderLiveDrops() {
    if (!els.liveDropsTrack || state.liveDrops.length === 0) return;

    els.liveDropsTrack.innerHTML = state.liveDrops.map(d => `
        <div class="live-drop-card ${d.rarity}">
            <span class="ld-icon">${d.item_icon}</span>
            <div class="ld-info">
                <span class="ld-name">${d.item_name}</span>
                <span class="ld-stars">${d.stars_value} ⭐</span>
            </div>
        </div>
    `).join('');
}

function renderCasesGrid(filter = 'all') {
    if (!els.casesGrid) return;

    let filtered = state.cases;
    if (filter === 'stars_14') {
        filtered = state.cases.filter(c => c.price === 14);
    } else if (filter === 'free') {
        filtered = state.cases.filter(c => c.price === 0);
    } else if (filter === 'vip') {
        filtered = state.cases.filter(c => c.category === 'vip');
    } else if (filter === 'gifts') {
        filtered = state.cases.filter(c => c.category === 'gifts' || c.category === 'stars_14');
    }

    if (filter === 'shop') {
        els.casesGrid.style.display = 'none';
        document.getElementById("shop-catalog-section").style.display = 'block';
        return;
    } else {
        els.casesGrid.style.display = 'grid';
        document.getElementById("shop-catalog-section").style.display = 'block';
    }

    els.casesGrid.innerHTML = filtered.map(c => {
        const btnText = c.price === 0 ? "Bepul Ochish" : `${c.price} ⭐ Ochish`;
        const btnClass = c.price === 0 ? "btn-case-open free-btn" : "btn-case-open";
        
        // Show first 4 item previews
        const previewItems = (c.items || []).slice(0, 4).map(it => `
            <span class="case-drop-bubble" title="${it.name}">${it.icon}</span>
        `).join('');

        return `
            <div id="card-${c.id}" class="case-card" onclick="openRouletteModal('${c.id}')">
                <span class="case-badge-top">${c.badge}</span>
                <div class="case-visual-wrapper">
                    <div class="case-glow-circle" style="background: ${c.glow_color}"></div>
                    <span class="case-3d-icon">${c.icon}</span>
                </div>
                <h4 class="case-title">${c.name}</h4>
                <div class="case-mini-drops">
                    ${previewItems}
                </div>
                <button class="${btnClass}">${btnText}</button>
            </div>
        `;
    }).join('');
}

function filterCases(category, pillElement) {
    triggerHaptic('light');
    document.querySelectorAll(".cat-pill").forEach(p => p.classList.remove("active"));
    if (pillElement) pillElement.classList.add("active");
    renderCasesGrid(category);
}

function renderInventory() {
    const container = document.getElementById("user-inventory-grid");
    if (!container) return;

    if (state.inventory.length === 0) {
        container.innerHTML = `
            <div class="empty-inventory">
                <div class="empty-icon-box">🎒</div>
                <h3>Inventaringiz bo'sh</h3>
                <p>14 Starsga Case oching va Telegram Giftlarni yutib oling!</p>
                <button class="btn-primary" onclick="switchTab('cases')" style="margin-top: 12px; width: auto; padding: 8px 18px;">
                    Keys ochishga o'tish 🚀
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = state.inventory.map(item => `
        <div class="inv-card">
            <span class="inv-icon">${item.icon}</span>
            <span class="inv-name">${item.name}</span>
            <span class="inv-stars">${item.stars_value} Stars</span>
            <div class="inv-actions">
                <button class="btn-inv-action sell" onclick="sellInventoryDirect(${item.id})">Sotish ⭐</button>
                <button class="btn-inv-action claim" onclick="openClaimModal(${item.id})">Olish 🎁</button>
            </div>
        </div>
    `).join('');
}

function renderCatalog() {
    if (!els.starsCatalog || !els.premiumCatalog) return;
    const stars = state.packages.filter(p => p.category === 'stars');
    const premium = state.packages.filter(p => p.category === 'premium');

    els.starsCatalog.innerHTML = stars.map(p => `
        <div class="catalog-card">
            <div class="catalog-card-icon">🌟</div>
            <div class="catalog-card-name">${p.name}</div>
            <div class="catalog-card-price">${p.price.toLocaleString('uz-UZ')} UZS</div>
            <button class="btn-buy" onclick="openBuyModal(${p.id})">Sotib olish</button>
        </div>
    `).join('');

    els.premiumCatalog.innerHTML = premium.map(p => `
        <div class="catalog-card">
            <div class="catalog-card-icon">💎</div>
            <div class="catalog-card-name">${p.name}</div>
            <div class="catalog-card-price">${p.price.toLocaleString('uz-UZ')} UZS</div>
            <button class="btn-buy" onclick="openBuyModal(${p.id})">Sotib olish</button>
        </div>
    `).join('');
}

// ==========================================================================
// 6. ROULETTE / CASE OPENING MECHANIC (CS:GO / TAPE STYLE)
// ==========================================================================

function openRouletteModal(caseId) {
    triggerHaptic('medium');
    const c = state.cases.find(x => x.id === caseId);
    if (!c) return;

    state.activeCase = c;
    document.getElementById("rm-case-icon").textContent = c.icon;
    document.getElementById("rm-case-name").textContent = c.name;
    document.getElementById("rm-case-price").textContent = c.price === 0 ? "Bepul" : `${c.price} ⭐`;

    const btnText = c.price === 0 ? "Bepul Ochish" : `${c.price} ⭐ Keysni Ochish`;
    document.getElementById("spin-button-text").textContent = btnText;

    // Populate contents preview
    const previewContainer = document.getElementById("case-preview-items");
    previewContainer.innerHTML = (c.items || []).map(it => `
        <div class="cpi-card ${it.rarity}">
            <span class="cpi-icon">${it.icon}</span>
            <span class="cpi-stars">${it.stars} ⭐</span>
        </div>
    `).join('');

    // Pre-populate tape with items
    initTapePreview(c);

    document.getElementById("roulette-modal").classList.add("active");
}

function initTapePreview(c) {
    const tape = document.getElementById("roulette-tape");
    tape.style.transition = 'none';
    tape.style.transform = 'translateX(0)';

    const items = c.items || [];
    let html = '';
    for (let i = 0; i < 20; i++) {
        const it = items[i % items.length];
        html += `
            <div class="tape-item-card ${it.rarity}">
                <span class="tape-item-icon">${it.icon}</span>
                <span class="tape-item-name">${it.name}</span>
                <span class="tape-item-stars">${it.stars} ⭐</span>
            </div>
        `;
    }
    tape.innerHTML = html;
}

function closeRouletteModal() {
    if (state.isSpinning) return;
    document.getElementById("roulette-modal").classList.remove("active");
    state.activeCase = null;
}

async function triggerCaseSpin() {
    if (state.isSpinning || !state.activeCase) return;
    const c = state.activeCase;

    // Stars validation
    if (c.price > 0 && state.user.stars_balance < c.price) {
        showToast(`Stars yetarli emas! Sizda ${Math.floor(state.user.stars_balance)} ⭐ bor, narxi: ${c.price} ⭐.`);
        openConvertModal();
        return;
    }

    const spinBtn = document.getElementById("btn-spin-case");
    spinBtn.disabled = true;
    state.isSpinning = true;

    try {
        const res = await fetch('/api/case/open', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                case_id: c.id
            })
        });

        if (!res.ok) {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi!");
            spinBtn.disabled = false;
            state.isSpinning = false;
            return;
        }

        const data = await res.json();
        state.user.stars_balance = data.new_stars_balance;
        updateBalancesUI();

        state.currentWonItem = data.winning_item;

        // Build the animated tape with 50 items
        renderAndSpinTape(data.tape, data.target_index);
    } catch (e) {
        console.error("Spin error:", e);
        showToast("Server bilan bog'lanishda xatolik!");
        spinBtn.disabled = false;
        state.isSpinning = false;
    }
}

function renderAndSpinTape(tapeItems, targetIndex) {
    const tape = document.getElementById("roulette-tape");
    const fastSpin = document.getElementById("fast-spin-toggle").checked;

    // Reset tape position
    tape.style.transition = 'none';
    tape.style.transform = 'translateX(0)';

    // Build DOM
    tape.innerHTML = tapeItems.map(it => `
        <div class="tape-item-card ${it.rarity}">
            <span class="tape-item-icon">${it.icon}</span>
            <span class="tape-item-name">${it.name}</span>
            <span class="tape-item-stars">${it.stars} ⭐</span>
        </div>
    `).join('');

    // Force reflow
    void tape.offsetWidth;

    // Card width = 90px + 10px margin = 100px
    const cardWidth = 100;
    const viewportWidth = tape.parentElement.offsetWidth || 380;
    const centerOffset = viewportWidth / 2;

    // Slight random offset inside the winning card (-20px to +20px)
    const randomShift = (Math.random() * 40) - 20;
    const targetScroll = (targetIndex * cardWidth) + (cardWidth / 2) - centerOffset + randomShift;

    const duration = fastSpin ? 1.2 : 5.0; // seconds
    tape.style.transition = `transform ${duration}s cubic-bezier(0.12, 0.8, 0.2, 1)`;
    tape.style.transform = `translateX(-${targetScroll}px)`;

    // Audio & Haptic ticking interval
    const totalTicks = fastSpin ? 15 : 45;
    let tickCount = 0;
    const tickInterval = setInterval(() => {
        tickCount++;
        playTickSound();
        triggerHaptic('light');
        if (tickCount >= totalTicks) {
            clearInterval(tickInterval);
        }
    }, (duration * 1000) / totalTicks);

    // On spin complete
    setTimeout(() => {
        clearInterval(tickInterval);
        triggerHaptic('success');
        playWinFanfare();

        state.isSpinning = false;
        document.getElementById("btn-spin-case").disabled = false;

        // Show Win Celebration
        openWinModal(state.currentWonItem);
        fetchInventory();
        fetchLiveDrops();
    }, (duration * 1000) + 200);
}

// 7. WOW Win Celebration Modal
function openWinModal(item) {
    document.getElementById("win-rarity-badge").textContent = `${item.rarity_label || 'YUTUQ'}!`;
    document.getElementById("win-item-icon").textContent = item.icon;
    document.getElementById("win-item-name").textContent = item.name;
    document.getElementById("win-item-stars").textContent = `${item.stars} Stars`;
    document.getElementById("btn-sell-subtext").textContent = `+${item.stars} Stars qo'shiladi`;

    const glow = document.getElementById("win-item-glow");
    glow.style.background = item.color || "#f59e0b";

    // Confetti explosion
    if (window.confetti) {
        window.confetti({
            particleCount: 120,
            spread: 80,
            origin: { y: 0.6 }
        });
    }

    document.getElementById("win-modal").classList.add("active");
}

function closeWinModal() {
    document.getElementById("win-modal").classList.remove("active");
}

async function sellWonItem() {
    if (!state.currentWonItem || !state.currentWonItem.inventory_id) {
        closeWinModal();
        return;
    }

    try {
        const res = await fetch('/api/inventory/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                item_id: state.currentWonItem.inventory_id
            })
        });

        if (res.ok) {
            const data = await res.json();
            state.user.stars_balance = data.new_stars_balance;
            updateBalancesUI();
            showToast(`+${data.stars_added} Stars balansingizga qo'shildi! 🌟`);
            closeWinModal();
            fetchInventory();
        }
    } catch (e) {
        console.error("sellWonItem error:", e);
    }
}

function keepWonItem() {
    triggerHaptic('success');
    showToast("Sovg'a inventaringizda saqlandi! 🎒");
    closeWinModal();
    fetchInventory();
}

function spinAgainFromWin() {
    closeWinModal();
    if (state.activeCase) {
        triggerCaseSpin();
    }
}

async function sellInventoryDirect(itemId) {
    triggerHaptic('medium');
    try {
        const res = await fetch('/api/inventory/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                item_id: itemId
            })
        });

        if (res.ok) {
            const data = await res.json();
            state.user.stars_balance = data.new_stars_balance;
            updateBalancesUI();
            showToast(`+${data.stars_added} Stars balansingizga qo'shildi! 🌟`);
            fetchInventory();
        }
    } catch (e) {
        console.error("sellInventoryDirect error:", e);
    }
}

// 8. Claim Gift to Telegram Account
let currentClaimItemId = null;
function openClaimModal(itemId) {
    currentClaimItemId = itemId;
    const item = state.inventory.find(x => x.id === itemId);
    if (!item) return;

    document.getElementById("claim-gift-icon").textContent = item.icon;
    document.getElementById("claim-gift-name").textContent = item.name;
    document.getElementById("claim-gift-stars").textContent = `${item.stars_value} Stars`;
    document.getElementById("claim-target-input").value = state.user.username || '';

    document.getElementById("claim-modal").classList.add("active");
}

function closeClaimModal() {
    document.getElementById("claim-modal").classList.remove("active");
    currentClaimItemId = null;
}

async function submitClaimGift() {
    const target = document.getElementById("claim-target-input").value.trim();
    if (!target) {
        showToast("Iltimos, Telegram username yoki ID kiriting!");
        return;
    }

    try {
        const res = await fetch('/api/inventory/claim', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                item_id: currentClaimItemId,
                target: target
            })
        });

        if (res.ok) {
            showToast("Sovg'ani yuborish so'rovi adminga jo'natildi! 🚀");
            closeClaimModal();
            fetchInventory();
        } else {
            showToast("Xatolik yuz berdi!");
        }
    } catch (e) {
        console.error("submitClaimGift error:", e);
    }
}

// 9. Wheel of Fortune (Omad Charxi)
const WHEEL_PRIZES = [
    { text: "🍪 362 ⭐", value: 362, color: "#d946ef", icon: "🍪" },
    { text: "10 ⭐", value: 10, color: "#f59e0b", icon: "⭐" },
    { text: "👑 250 ⭐", value: 250, color: "#eab308", icon: "👑" },
    { text: "🧸 15 ⭐", value: 15, color: "#0284c7", icon: "🧸" },
    { text: "🍾 100 ⭐", value: 100, color: "#a855f7", icon: "🍾" },
    { text: "💖 15 ⭐", value: 15, color: "#38bdf8", icon: "💖" },
    { text: "🎂 50 ⭐", value: 50, color: "#c084fc", icon: "🎂" },
    { text: "🌹 25 ⭐", value: 25, color: "#f43f5e", icon: "🌹" },
];

let wheelAngle = 0;
let isWheelSpinning = false;

function initWheelCanvas() {
    const canvas = document.getElementById("wheel-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const numSlices = WHEEL_PRIZES.length;
    const sliceAngle = (2 * Math.PI) / numSlices;
    const radius = canvas.width / 2;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < numSlices; i++) {
        const angle = i * sliceAngle;
        ctx.beginPath();
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius, angle, angle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = WHEEL_PRIZES[i].color;
        ctx.fill();
        ctx.strokeStyle = "rgba(0,0,0,0.4)";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw text
        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(angle + sliceAngle / 2);
        ctx.textAlign = "right";
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 13px Outfit, sans-serif";
        ctx.shadowColor = "rgba(0,0,0,0.8)";
        ctx.shadowBlur = 4;
        ctx.fillText(WHEEL_PRIZES[i].text, radius - 15, 5);
        ctx.restore();
    }
}

async function spinWheel() {
    if (isWheelSpinning) return;
    if (state.user.stars_balance < 10) {
        showToast("Omad charxini aylantirish uchun 10 ⭐ kerak!");
        openConvertModal();
        return;
    }

    const btn = document.getElementById("btn-spin-wheel");
    btn.disabled = true;
    isWheelSpinning = true;

    // Deduct 10 stars locally
    state.user.stars_balance -= 10;
    updateBalancesUI();

    const canvas = document.getElementById("wheel-canvas");
    const winningIndex = Math.floor(Math.random() * WHEEL_PRIZES.length);
    const numSlices = WHEEL_PRIZES.length;
    const sliceDeg = 360 / numSlices;

    // Pointer is at the top (270 degrees)
    const targetDeg = (360 - (winningIndex * sliceDeg) - (sliceDeg / 2) + 270) % 360;
    const totalRotation = (5 * 360) + targetDeg; // 5 full spins + target

    canvas.style.transition = 'transform 5s cubic-bezier(0.12, 0.8, 0.2, 1)';
    canvas.style.transform = `rotate(${totalRotation}deg)`;

    // Tick audio
    let ticks = 0;
    const tickInterval = setInterval(() => {
        ticks++;
        playTickSound();
        triggerHaptic('light');
        if (ticks >= 40) clearInterval(tickInterval);
    }, 120);

    setTimeout(async () => {
        clearInterval(tickInterval);
        isWheelSpinning = false;
        btn.disabled = false;
        triggerHaptic('success');
        playWinFanfare();

        const won = WHEEL_PRIZES[winningIndex];
        // Add prize
        state.user.stars_balance += won.value;
        updateBalancesUI();

        openWinModal({
            name: `Omad Charxi: ${won.text}`,
            icon: won.icon,
            stars: won.value,
            rarity: won.value > 100 ? 'epic' : 'rare',
            rarity_label: 'Omad Charxi Yutug\'i',
            color: won.color
        });
    }, 5200);
}

// 10. Convert UZS to Stars Modal
function openConvertModal() {
    triggerHaptic('light');
    selectConvertPreset(25);
    document.getElementById("convert-modal").classList.add("active");
}

function closeConvertModal() {
    document.getElementById("convert-modal").classList.remove("active");
}

function selectConvertPreset(stars) {
    document.querySelectorAll(".qsp-btn").forEach(b => b.classList.remove("active"));
    const input = document.getElementById("convert-stars-input");
    if (input) input.value = stars;
    updateConvertCalc();
}

function updateConvertCalc() {
    const input = document.getElementById("convert-stars-input");
    const val = parseInt(input.value) || 0;
    const totalUzs = val * 280;
    document.getElementById("convert-total-uzs").textContent = `${totalUzs.toLocaleString('uz-UZ')} UZS`;
}

async function executeConvertStars() {
    const input = document.getElementById("convert-stars-input");
    const stars = parseInt(input.value) || 0;
    if (stars <= 0) return;

    const totalUzs = stars * 280;
    if (state.user.balance < totalUzs) {
        showToast(`Balansingizda mablag' yetarli emas! ${totalUzs.toLocaleString('uz-UZ')} UZS kerak.`);
        switchProfileSection('deposit');
        closeConvertModal();
        return;
    }

    try {
        const res = await fetch('/api/convert_uzs_to_stars', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                stars_amount: stars
            })
        });

        if (res.ok) {
            const data = await res.json();
            state.user.stars_balance = data.new_stars_balance;
            state.user.balance = data.new_uzs_balance;
            updateBalancesUI();
            showToast(`Muvaffaqiyatli! +${stars} ⭐ balansingizga tushdi! 🚀`);
            closeConvertModal();
        } else {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi!");
        }
    } catch (e) {
        console.error("executeConvertStars error:", e);
    }
}

// 11. Deposit Submission (Chek yuklash)
let receiptBase64 = null;
let receiptFileName = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
        showToast("Rasm hajmi juda katta! Maksimal 10MB bo'lishi kerak.");
        event.target.value = '';
        return;
    }

    receiptFileName = file.name;
    document.getElementById("upload-status-text").textContent = `Tanlandi: ${file.name}`;

    const reader = new FileReader();
    reader.onload = function(e) {
        receiptBase64 = e.target.result;
        const preview = document.getElementById("receipt-preview");
        preview.src = e.target.result;
        preview.style.display = "block";
        document.getElementById("upload-trigger").style.display = "none";
    };
    reader.readAsDataURL(file);
}

function copyCardNumber() {
    triggerHaptic('light');
    const cardNum = state.settings.cardNumber.replace(/\s+/g, '');
    navigator.clipboard.writeText(cardNum).then(() => {
        showToast("Karta raqami nusxalandi!");
    }).catch(() => {
        showToast("Karta raqami nusxalandi!");
    });
}

async function submitDeposit() {
    const amountInput = document.getElementById("deposit-amount");
    const amount = parseFloat(amountInput.value);

    if (isNaN(amount) || amount < 5000) {
        showToast("Iltimos, kamida 5,000 UZS kiriting!");
        return;
    }

    if (!receiptBase64) {
        showToast("Iltimos, to'lov chekini yuklang!");
        return;
    }

    const btn = document.getElementById("btn-submit-deposit");
    btn.disabled = true;
    btn.textContent = "Yuborilmoqda...";

    try {
        const res = await fetch('/api/deposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                amount: amount,
                payment_method: 'manual',
                receipt_base64: receiptBase64,
                file_name: receiptFileName
            })
        });

        if (res.ok) {
            showToast("To'lov tekshirishga yuborildi! Admin tasdiqlagach balansga tushadi ✅");
            amountInput.value = '';
            receiptBase64 = null;
            document.getElementById("receipt-preview").style.display = "none";
            document.getElementById("upload-trigger").style.display = "flex";
            document.getElementById("upload-status-text").textContent = "Chek rasmini tanlang";
            switchProfileSection('history');
        } else {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi!");
        }
    } catch (e) {
        console.error("submitDeposit error:", e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="send"></i> To'lovni tekshirishga yuborish`;
        if (window.lucide) window.lucide.createIcons();
    }
}

// 12. History Tab
async function fetchHistory() {
    try {
        const res = await fetch(`/api/history?user_id=${state.user.id}`);
        if (res.ok) {
            const data = await res.json();
            state.history.orders = data.orders || [];
            state.history.deposits = data.deposits || [];
            renderHistory();
        }
    } catch (e) {
        console.error("fetchHistory error:", e);
    }
}

function renderHistory() {
    const container = document.getElementById("history-container");
    if (!container) return;

    const all = [
        ...state.history.orders.map(o => ({ ...o, type: 'order' })),
        ...state.history.deposits.map(d => ({ ...d, type: 'deposit' }))
    ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    if (all.length === 0) {
        container.innerHTML = `
            <div class="empty-inventory">
                <div class="empty-icon-box">📜</div>
                <h3>Tarix hali bo'sh</h3>
                <p>Buyurtmalar va to'lovlar shu yerda ko'rinadi.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = all.map(item => {
        const isOrder = item.type === 'order';
        const title = isOrder ? item.package_name : "Balans to'ldirish";
        const price = isOrder ? `-${(item.price || 0).toLocaleString()} UZS` : `+${(item.amount || 0).toLocaleString()} UZS`;
        let statusClass = "status-pending";
        let statusText = "Kutilmoqda";

        if (item.status === 'completed' || item.status === 'approved') {
            statusClass = "status-completed";
            statusText = "Bajarildi";
        } else if (item.status === 'cancelled' || item.status === 'rejected') {
            statusClass = "status-cancelled";
            statusText = "Rad etildi";
        }

        return `
            <div class="history-card">
                <div class="hc-left">
                    <span class="hc-title">${title}</span>
                    <span class="hc-date">${item.created_at || ''}</span>
                </div>
                <div class="hc-right">
                    <span class="hc-price">${price}</span>
                    <span class="hc-status ${statusClass}">${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 13. Purchase Modal for Catalog (Stars/Premium)
let selectedPackage = null;
function openBuyModal(pkgId) {
    const pkg = state.packages.find(p => p.id === pkgId);
    if (!pkg) return;
    selectedPackage = pkg;

    document.getElementById("modal-prod-icon").textContent = pkg.category === 'stars' ? '🌟' : '💎';
    document.getElementById("modal-prod-name").textContent = pkg.name;
    document.getElementById("modal-prod-price").textContent = `${pkg.price.toLocaleString('uz-UZ')} UZS`;

    const userBal = state.user.balance || 0;
    document.getElementById("modal-user-balance").textContent = `Mening balansim: ${userBal.toLocaleString('uz-UZ')} UZS`;

    const statusEl = document.getElementById("modal-balance-status");
    const confirmBtn = document.getElementById("btn-confirm-purchase");

    if (userBal >= pkg.price) {
        statusEl.textContent = "Yetarli";
        statusEl.className = "wpc-status status-success";
        confirmBtn.disabled = false;
    } else {
        statusEl.textContent = "Yetarli emas";
        statusEl.className = "wpc-status status-rejected";
        confirmBtn.disabled = true;
    }

    document.getElementById("buy-modal").classList.add("active");
}

function closeBuyModal() {
    document.getElementById("buy-modal").classList.remove("active");
    selectedPackage = null;
}

async function confirmPurchase() {
    const target = document.getElementById("order-target").value.trim();
    if (!target) {
        showToast("Iltimos, username yoki telefon raqam kiriting!");
        return;
    }

    if (!selectedPackage) return;

    try {
        const res = await fetch('/api/purchase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                username: state.user.username,
                first_name: state.user.first_name,
                package_id: selectedPackage.id,
                target_username: target
            })
        });

        if (res.ok) {
            const data = await res.json();
            state.user.balance = data.new_balance;
            updateBalancesUI();
            showToast("Buyurtma qabul qilindi va tekshirilmoqda! 🚀");
            closeBuyModal();
            switchProfileSection('history');
        } else {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi!");
        }
    } catch (e) {
        console.error("confirmPurchase error:", e);
    }
}

// 14. Helper Toast
function showToast(msg) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    document.getElementById("toast-message").textContent = msg;
    toast.classList.add("active");
    setTimeout(() => {
        toast.classList.remove("active");
    }, 3200);
}
