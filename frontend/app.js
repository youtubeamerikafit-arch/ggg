// ==========================================================================
// MINE — AntiGravity (v1.2) | Application Logic & Ruletka
// ==========================================================================

const tg = window.Telegram ? window.Telegram.WebApp : null;

// Application State
let state = {
    user: {
        id: 5721221489,
        display_id: "mine_user_99", // Talab qilingan format: ID: mine_user_99
        first_name: "IBROHIM",
        username: "@IBROHIMBOI_UC",
        photo_url: "https://img.icons8.com/color/96/avatar.png",
        balance: 0,
        completed_orders: 0,
        reg_date: "26.07.2026"
    },
    packages: [],
    history: {
        orders: [],
        deposits: []
    },
    selectedPackage: null,
    selectedCase: null,
    currentWonWeapon: null,
    isSpinning: false,
    settings: {
        cardNumber: "9860 6004 0697 7147",
        cardOwner: "XUJAMURATOVA ZARGUL",
        newsLink: "https://t.me/YAKUDZA_UC_NEWS",
        supportLink: "https://t.me/yakfast_support"
    }
};

// Cursed Island Cases Data
const CURSED_CASES = {
    flamingo: {
        id: "flamingo",
        name: "Flamingo Keysi",
        icon: "🦩",
        price: 15000,
        desc: "Pushti flamingo kamoni va noyob tropik qurollar!",
        weapons: [
            { name: "Pushti Flamingo Kamoni", icon: "🏹", value: 15000, rarity: "rare" },
            { name: "Flamingo Xanjari", icon: "🗡️", value: 18000, rarity: "rare" },
            { name: "Tropik Nayza", icon: "🔱", value: 12000, rarity: "common" },
            { name: "Qora Olmos Xanjari", icon: "💎", value: 80000, rarity: "mythic" }
        ]
    },
    volcano: {
        id: "volcano",
        name: "Vulqon Keysi",
        icon: "🌋",
        price: 25000,
        desc: "Olovli Vulqon AK-47 va Magma pistoletlari!",
        weapons: [
            { name: "Olovli Vulqon AK-47", icon: "🔫", value: 35000, rarity: "epic" },
            { name: "Magma Pistoleti", icon: "💥", value: 25000, rarity: "rare" },
            { name: "Olovli Qilich", icon: "⚔️", value: 50000, rarity: "legendary" },
            { name: "Lava Pichoq", icon: "🔪", value: 10000, rarity: "common" }
        ]
    },
    cursed: {
        id: "cursed",
        name: "La’natlangan Orol Keysi",
        icon: "🌴",
        price: 40000,
        desc: "La'natlangan machete va zaharli artefaktlar!",
        weapons: [
            { name: "La'natlangan Machete", icon: "🗡️", value: 20000, rarity: "rare" },
            { name: "Zaharli Nayza", icon: "🔱", value: 12000, rarity: "common" },
            { name: "Qora Olmos Xanjari", icon: "💎", value: 80000, rarity: "mythic" },
            { name: "Oltin Qilich", icon: "⚔️", value: 50000, rarity: "legendary" }
        ]
    },
    temple: {
        id: "temple",
        name: "Qadimiy Ma’bada Keysi",
        icon: "🗿",
        price: 60000,
        desc: "Qadimiy qabila qurollari va afsonaviy xazinasi!",
        weapons: [
            { name: "Qora Olmos Xanjari", icon: "💎", value: 80000, rarity: "mythic" },
            { name: "Oltin Qilich", icon: "⚔️", value: 50000, rarity: "legendary" },
            { name: "Olovli Vulqon AK-47", icon: "🔫", value: 35000, rarity: "epic" },
            { name: "Pushti Flamingo Kamoni", icon: "🏹", value: 15000, rarity: "rare" }
        ]
    }
};

// Ruletka Qurollari
const ROULETTE_WEAPONS = [
    { name: "Pushti Flamingo Kamoni", icon: "🏹", value: 15000, rarity: "rare" },
    { name: "Olovli Vulqon AK-47", icon: "🔫", value: 35000, rarity: "epic" },
    { name: "La'natlangan Machete", icon: "🗡️", value: 20000, rarity: "rare" },
    { name: "Zaharli Nayza", icon: "🔱", value: 12000, rarity: "common" },
    { name: "Magma Pistoleti", icon: "💥", value: 25000, rarity: "rare" },
    { name: "Qora Olmos Xanjari", icon: "💎", value: 80000, rarity: "mythic" },
    { name: "Tropik Pichoq", icon: "🔪", value: 8000, rarity: "common" },
    { name: "Oltin Qilich", icon: "⚔️", value: 50000, rarity: "legendary" }
];

// DOM Cache
const els = {};

document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) window.lucide.createIcons();

    // Cache elements
    els.userAvatar = document.getElementById("user-avatar");
    els.profileAvatar = document.getElementById("profile-avatar");
    els.userDisplayName = document.getElementById("user-display-name");
    els.headerUserId = document.getElementById("header-user-id");
    els.profileName = document.getElementById("profile-name");
    els.profileUsername = document.getElementById("profile-username");
    els.profileId = document.getElementById("profile-id");

    els.mainBalance = document.getElementById("main-balance-amount");
    els.depositBalance = document.getElementById("deposit-balance-amount");
    els.profileBalance = document.getElementById("profile-balance-display");

    els.starsCatalog = document.getElementById("stars-catalog");
    els.premiumCatalog = document.getElementById("premium-catalog");

    els.statsOrders = document.getElementById("stats-orders");
    els.statsRegDate = document.getElementById("stats-reg-date");
    els.linkNews = document.getElementById("link-news");
    els.linkSupport = document.getElementById("link-support");

    els.cardNumber = document.getElementById("card-number");
    els.cardOwner = document.getElementById("card-owner");

    els.buyModal = document.getElementById("buy-modal");
    els.toast = document.getElementById("toast");

    // Init Telegram WebApp Data
    initTelegramData();

    // Fetch API Data
    fetchUserData();
    fetchCatalog();

    // Initial Render
    renderProfile();
});

// 1. Telegram WebApp Integration
function initTelegramData() {
    if (!tg) return;
    tg.ready();
    tg.expand();

    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        const u = tg.initDataUnsafe.user;
        state.user.id = u.id;
        state.user.first_name = u.first_name || "IBROHIM";
        state.user.username = u.username ? `@${u.username}` : "@IBROHIMBOI_UC";
        state.user.display_id = `mine_user_${u.id % 1000 || 99}`;
        state.user.photo_url = u.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(state.user.first_name)}&background=1e293b&color=ffffff&size=128`;
    }
}

// 2. Navigation
function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".nav-tab-btn").forEach(el => el.classList.remove("active"));

    const tabEl = document.getElementById(`tab-${tabId}`);
    if (tabEl) tabEl.classList.add("active");

    const tabsList = ['home', 'balance', 'history', 'profile'];
    const idx = tabsList.indexOf(tabId);
    if (idx !== -1) {
        document.querySelectorAll(".nav-tab-btn")[idx].classList.add("active");
    }

    if (tabId === 'history') {
        fetchHistory();
    }
    if (tabId === 'balance' || tabId === 'profile') {
        fetchUserData();
    }
}

function switchHistorySubTab(subTab) {
    document.querySelectorAll(".history-tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".history-list-container").forEach(c => c.classList.remove("active"));

    if (subTab === 'orders') {
        document.querySelectorAll(".history-tab-btn")[0].classList.add("active");
        document.getElementById("history-orders-container").classList.add("active");
    } else {
        document.querySelectorAll(".history-tab-btn")[1].classList.add("active");
        document.getElementById("history-deposits-container").classList.add("active");
    }
}

function scrollToCursedCases() {
    switchTab('home');
    setTimeout(() => {
        const el = document.getElementById("cursed-cases-section");
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 150);
}

// 3. UI Rendering & Balances (Faqat va faqat UZS)
function renderProfile() {
    if (els.userAvatar) els.userAvatar.src = state.user.photo_url;
    if (els.profileAvatar) els.profileAvatar.src = state.user.photo_url;
    if (els.userDisplayName) els.userDisplayName.textContent = state.user.first_name;
    
    // Foydalanuvchi IDsi: "ID: mine_user_99"
    if (els.headerUserId) els.headerUserId.textContent = `ID: ${state.user.display_id}`;
    if (els.profileId) els.profileId.textContent = `ID: ${state.user.display_id}`;

    if (els.profileName) els.profileName.textContent = state.user.first_name;
    if (els.profileUsername) els.profileUsername.textContent = state.user.username;

    updateBalancesUI();

    if (els.statsOrders) els.statsOrders.textContent = state.user.completed_orders;
    if (els.statsRegDate) els.statsRegDate.textContent = state.user.reg_date;

    if (els.linkNews) els.linkNews.href = state.settings.newsLink;
    if (els.linkSupport) els.linkSupport.href = state.settings.supportLink;

    if (els.cardNumber) els.cardNumber.textContent = state.settings.cardNumber;
    if (els.cardOwner) els.cardOwner.textContent = state.settings.cardOwner;
}

function updateBalancesUI() {
    const formatted = `${(state.user.balance || 0).toLocaleString('uz-UZ')} UZS`;
    if (els.mainBalance) els.mainBalance.textContent = formatted;
    if (els.depositBalance) els.depositBalance.textContent = formatted;
    if (els.profileBalance) els.profileBalance.textContent = formatted;

    const rUserBal = document.getElementById("roulette-user-balance");
    if (rUserBal) rUserBal.textContent = formatted;

    const cUserBal = document.getElementById("case-user-balance");
    if (cUserBal) cUserBal.textContent = formatted;
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

// 4. API Requests
async function fetchUserData() {
    try {
        const res = await fetch(`/api/user?user_id=${state.user.id}`);
        if (res.ok) {
            const data = await res.json();
            state.user.balance = data.balance || 0;
            state.user.completed_orders = data.completed_orders || 0;
            state.user.reg_date = data.joined_at_formatted || state.user.reg_date;
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

async function fetchCatalog() {
    try {
        const res = await fetch('/api/packages');
        if (res.ok) {
            state.packages = await res.json();
            renderCatalog();
        }
    } catch (e) {
        console.error("fetchCatalog fallback:", e);
        state.packages = [
            { id: 1, category: 'stars', name: '100 Stars 🌟', price: 28000, value: 100 },
            { id: 2, category: 'stars', name: '150 Stars 🌟', price: 41000, value: 150 },
            { id: 3, category: 'stars', name: '250 Stars 🌟', price: 66000, value: 250 },
            { id: 4, category: 'stars', name: '500 Stars 🌟', price: 130000, value: 500 },
            { id: 5, category: 'stars', name: '1000 Stars 🌟', price: 257000, value: 1000 },
            { id: 6, category: 'premium', name: 'Premium 3 Oylik 💎', price: 90000, value: 3 },
            { id: 7, category: 'premium', name: 'Premium 6 Oylik 💎', price: 160000, value: 6 },
            { id: 8, category: 'premium', name: 'Premium 12 Oylik 💎', price: 290000, value: 12 },
        ];
        renderCatalog();
    }
}

async function fetchHistory() {
    try {
        const res = await fetch(`/api/history?user_id=${state.user.id}`);
        if (res.ok) {
            const data = await res.json();
            state.history.orders = data.orders || [];
            state.history.deposits = data.deposits || [];
            renderHistoryLists();
        }
    } catch (e) {
        console.error("fetchHistory error:", e);
        renderHistoryLists();
    }
}

function renderHistoryLists() {
    const ordersContainer = document.getElementById("history-orders-container");
    const depositsContainer = document.getElementById("history-deposits-container");

    if (state.history.orders.length === 0) {
        ordersContainer.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 24px;">
                <h3>Buyurtmalar hali yo'q</h3>
                <p style="font-size: 11px; color: var(--text-muted);">Buyurtmalar tarixingiz shu yerda ko'rinadi.</p>
            </div>
        `;
    } else {
        ordersContainer.innerHTML = state.history.orders.map(o => `
            <div class="history-card" data-search="${o.package_name.toLowerCase()}">
                <div class="hc-left">
                    <span class="hc-title">${o.package_name}</span>
                    <span class="hc-target">Kimga: ${o.target_username}</span>
                    <span class="hc-date">${o.created_at || ''}</span>
                </div>
                <div class="hc-right">
                    <span class="hc-price">${(o.price || 0).toLocaleString('uz-UZ')} UZS</span>
                    <span class="hc-status status-${o.status}">${o.status === 'completed' ? 'Bajarildi' : 'Kutilmoqda'}</span>
                </div>
            </div>
        `).join('');
    }

    if (state.history.deposits.length === 0) {
        depositsContainer.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 24px;">
                <h3>Tranzaksiyalar mavjud emas</h3>
                <p style="font-size: 11px; color: var(--text-muted);">To'lov tarixingiz shu yerda ko'rinadi.</p>
            </div>
        `;
    } else {
        depositsContainer.innerHTML = state.history.deposits.map(d => `
            <div class="history-card">
                <div class="hc-left">
                    <span class="hc-title">Balansni to'ldirish</span>
                    <span class="hc-target">Turi: ${(d.payment_method || 'karta').toUpperCase()}</span>
                    <span class="hc-date">${d.created_at || ''}</span>
                </div>
                <div class="hc-right">
                    <span class="hc-price">+${(d.amount || 0).toLocaleString('uz-UZ')} UZS</span>
                    <span class="hc-status status-${d.status}">${d.status === 'approved' ? 'Tasdiqlandi' : 'Kutilmoqda'}</span>
                </div>
            </div>
        `).join('');
    }
}

// ==========================================================================
// 5. ANIMATED RULETKA (Qurollar Ruletkasi)
// ==========================================================================

function openRouletteModal() {
    updateBalancesUI();
    initRouletteTrack();
    document.getElementById("roulette-modal").classList.add("active");
}

function closeRouletteModal() {
    if (state.isSpinning) return;
    document.getElementById("roulette-modal").classList.remove("active");
}

function initRouletteTrack() {
    const track = document.getElementById("roulette-track");
    track.style.transition = 'none';
    track.style.transform = 'translateX(0)';

    let html = '';
    for (let i = 0; i < 30; i++) {
        const w = ROULETTE_WEAPONS[i % ROULETTE_WEAPONS.length];
        html += `
            <div class="rt-item-card ${w.rarity}">
                <span class="rt-item-icon">${w.icon}</span>
                <span class="rt-item-name">${w.name}</span>
                <span class="rt-item-val">${w.value.toLocaleString('uz-UZ')} UZS</span>
            </div>
        `;
    }
    track.innerHTML = html;
}

async function spinRoulette() {
    if (state.isSpinning) return;
    const cost = 10000;

    if (state.user.balance < cost) {
        showToast(`Mablag' yetarli emas! Ruletka narxi: 10,000 UZS. Iltimos, hisobingizni to'ldiring.`);
        switchTab('balance');
        closeRouletteModal();
        return;
    }

    const btn = document.getElementById("btn-spin-roulette");
    btn.disabled = true;
    state.isSpinning = true;

    try {
        // Try backend API first
        const res = await fetch('/api/roulette/spin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                cost: cost
            })
        });

        let wonWeapon = null;
        if (res.ok) {
            const data = await res.json();
            state.user.balance = data.new_balance;
            wonWeapon = data.won_weapon;
        } else {
            // Local fallback simulation if endpoint not reached
            state.user.balance -= cost;
            wonWeapon = ROULETTE_WEAPONS[Math.floor(Math.random() * ROULETTE_WEAPONS.length)];
        }

        updateBalancesUI();
        state.currentWonWeapon = wonWeapon;

        // Perform smooth tape spin animation
        animateRouletteTrack(wonWeapon);

    } catch (e) {
        console.error("spinRoulette error:", e);
        // Local fallback
        state.user.balance -= cost;
        const wonWeapon = ROULETTE_WEAPONS[Math.floor(Math.random() * ROULETTE_WEAPONS.length)];
        state.currentWonWeapon = wonWeapon;
        updateBalancesUI();
        animateRouletteTrack(wonWeapon);
    }
}

function animateRouletteTrack(wonWeapon) {
    const track = document.getElementById("roulette-track");
    const targetIndex = 22; // Lands on item 22

    // Populate track with target winning weapon at targetIndex
    const items = [];
    for (let i = 0; i < 35; i++) {
        if (i === targetIndex) {
            items.push(wonWeapon);
        } else {
            items.push(ROULETTE_WEAPONS[Math.floor(Math.random() * ROULETTE_WEAPONS.length)]);
        }
    }

    track.innerHTML = items.map(w => `
        <div class="rt-item-card ${w.rarity}">
            <span class="rt-item-icon">${w.icon}</span>
            <span class="rt-item-name">${w.name}</span>
            <span class="rt-item-val">${w.value.toLocaleString('uz-UZ')} UZS</span>
        </div>
    `).join('');

    // Force reflow
    void track.offsetWidth;

    // Card width = 80px + 8px margin = 88px
    const cardWidth = 88;
    const viewportWidth = track.parentElement.offsetWidth || 340;
    const centerOffset = viewportWidth / 2;
    const targetScroll = (targetIndex * cardWidth) + (cardWidth / 2) - centerOffset;

    track.style.transition = 'transform 4.5s cubic-bezier(0.12, 0.8, 0.2, 1)';
    track.style.transform = `translateX(-${targetScroll}px)`;

    setTimeout(() => {
        state.isSpinning = false;
        document.getElementById("btn-spin-roulette").disabled = false;
        closeRouletteModal();
        openWonWeaponModal(wonWeapon);
    }, 4800);
}

// G'alaba qozonilganda
function openWonWeaponModal(weapon) {
    document.getElementById("won-weapon-icon").textContent = weapon.icon;
    document.getElementById("won-weapon-name").textContent = weapon.name;
    document.getElementById("won-weapon-value").textContent = `Qiymati: ${weapon.value.toLocaleString('uz-UZ')} UZS`;
    document.getElementById("won-sell-amount").textContent = weapon.value.toLocaleString('uz-UZ');
    document.getElementById("won-weapon-modal").classList.add("active");
}

function closeWonWeaponModal() {
    document.getElementById("won-weapon-modal").classList.remove("active");
}

async function sellWonWeapon() {
    if (!state.currentWonWeapon) return;
    const val = state.currentWonWeapon.value;

    try {
        await fetch('/api/roulette/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                value: val
            })
        });
    } catch (e) {}

    state.user.balance += val;
    updateBalancesUI();
    showToast(`Qurol sotildi! +${val.toLocaleString('uz-UZ')} UZS hisobingizga qo'shildi! 💰`);
    closeWonWeaponModal();
}

function keepWonWeapon() {
    showToast("Qurol inventaringizga saqlandi! ⚔️");
    closeWonWeaponModal();
}

// ==========================================================================
// 6. LA'NATLANGAN OROL KEYSLARI
// ==========================================================================

function openCaseModal(caseKey) {
    const c = CURSED_CASES[caseKey];
    if (!c) return;
    state.selectedCase = c;

    document.getElementById("case-modal-icon").textContent = c.icon;
    document.getElementById("case-modal-title").textContent = c.name;
    document.getElementById("case-modal-desc").textContent = c.desc;
    document.getElementById("case-modal-price").textContent = `${c.price.toLocaleString('uz-UZ')} UZS`;

    updateBalancesUI();
    document.getElementById("case-modal").classList.add("active");
}

function closeCaseModal() {
    document.getElementById("case-modal").classList.remove("active");
    state.selectedCase = null;
}

async function confirmOpenCase() {
    const c = state.selectedCase;
    if (!c) return;

    if (state.user.balance < c.price) {
        showToast(`Mablag' yetarli emas! ${c.name} narxi: ${c.price.toLocaleString('uz-UZ')} UZS.`);
        closeCaseModal();
        switchTab('balance');
        return;
    }

    state.user.balance -= c.price;
    updateBalancesUI();
    closeCaseModal();

    // Random weapon from this case
    const won = c.weapons[Math.floor(Math.random() * c.weapons.length)];
    state.currentWonWeapon = won;
    openWonWeaponModal(won);
}

// ==========================================================================
// 7. KIRISH KABINETI (LOGIN MODAL)
// ==========================================================================

function openLoginModal() {
    document.getElementById("login-user-name").textContent = state.user.first_name;
    document.getElementById("login-user-id").textContent = `ID: ${state.user.display_id}`;
    document.getElementById("login-user-balance").textContent = `${state.user.balance.toLocaleString('uz-UZ')} UZS`;
    document.getElementById("login-avatar-preview").src = state.user.photo_url;
    document.getElementById("login-modal").classList.add("active");
}

function closeLoginModal() {
    document.getElementById("login-modal").classList.remove("active");
}

// ==========================================================================
// 8. DEPOZIT VA CHEK YUKLASH
// ==========================================================================

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
            showToast("To'lov tekshirishga yuborildi! Admin tasdiqlagach hisobingizga tushadi ✅");
            amountInput.value = '';
            receiptBase64 = null;
            document.getElementById("receipt-preview").style.display = "none";
            document.getElementById("upload-trigger").style.display = "flex";
            document.getElementById("upload-status-text").textContent = "Chek rasmini tanlang";
            switchTab('history');
            switchHistorySubTab('deposits');
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

// ==========================================================================
// 9. STARS VA PREMIUM XARIDI (BUY MODAL)
// ==========================================================================

function openBuyModal(pkgId) {
    const pkg = state.packages.find(p => p.id === pkgId);
    if (!pkg) return;
    state.selectedPackage = pkg;

    document.getElementById("modal-prod-icon").textContent = pkg.category === 'stars' ? '🌟' : '💎';
    document.getElementById("modal-prod-name").textContent = pkg.name;
    document.getElementById("modal-prod-price").textContent = `${pkg.price.toLocaleString('uz-UZ')} UZS`;

    const userBal = state.user.balance || 0;
    document.getElementById("modal-user-balance").textContent = `Hisobingiz: ${userBal.toLocaleString('uz-UZ')} UZS`;

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
    state.selectedPackage = null;
}

async function confirmPurchase() {
    const target = document.getElementById("order-target").value.trim();
    if (!target) {
        showToast("Iltimos, username yoki telefon raqam kiriting!");
        return;
    }

    if (!state.selectedPackage) return;
    const pkg = state.selectedPackage;

    try {
        const res = await fetch('/api/purchase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                username: state.user.username,
                first_name: state.user.first_name,
                package_id: pkg.id,
                target_username: target
            })
        });

        if (res.ok) {
            const data = await res.json();
            state.user.balance = data.new_balance;
            updateBalancesUI();
            showToast("Buyurtma qabul qilindi va tekshirilmoqda! 🚀");
            closeBuyModal();
            switchTab('history');
        } else {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi!");
        }
    } catch (e) {
        console.error("confirmPurchase error:", e);
    }
}

// 10. Qidiruv va Filter
function filterHistory() {
    const searchVal = document.getElementById("history-search").value.toLowerCase();
    const cards = document.querySelectorAll(".history-card");

    cards.forEach(card => {
        const searchData = card.getAttribute("data-search");
        if (searchData && searchData.includes(searchVal)) {
            card.style.display = "flex";
        } else {
            card.style.display = "none";
        }
    });
}

function showToast(msg) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    document.getElementById("toast-message").textContent = msg;
    toast.classList.add("active");
    setTimeout(() => {
        toast.classList.remove("active");
    }, 3200);
}
