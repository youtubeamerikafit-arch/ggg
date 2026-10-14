// Initialize Telegram WebApp SDK
const tg = window.Telegram ? window.Telegram.WebApp : null;

// Application State
let state = {
    user: {
        id: 5721221489, // Mock default matching screenshot
        first_name: "IBROHIM",
        username: "IBROHIMBOI_UC",
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
    selectedPaymentMethod: 'manual',
    selectedPackage: null,
    receiptBase64: null,
    receiptFileName: null,
    settings: {
        cardNumber: "8600 1204 5678 9012",
        cardOwner: "IBROHIM KH.",
        newsLink: "https://t.me/YAKUDZA_UC_NEWS",
        supportLink: "https://t.me/yakfast_support"
    }
};

// DOM Elements cache
const els = {};

// Wait for DOM to load
document.addEventListener("DOMContentLoaded", () => {
    // Initialize icons
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Cache common DOM elements
    els.userAvatar = document.getElementById("user-avatar");
    els.profileAvatar = document.getElementById("profile-avatar");
    els.userDisplayName = document.getElementById("user-display-name");
    els.profileName = document.getElementById("profile-name");
    els.profileUsername = document.getElementById("profile-username");
    els.profileId = document.getElementById("profile-id");
    
    els.headerBalance = document.getElementById("header-balance-amount");
    els.mainBalance = document.getElementById("main-balance-amount");
    els.depositBalance = document.getElementById("deposit-balance-amount");
    
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
    
    // Parse Telegram WebApp Data
    initTelegramData();
    
    // Fetch Initial Data from API
    fetchUserData();
    fetchCatalog();
    
    // Initial UI render
    renderProfile();
    startCarousel();
});

// 1. Telegram WebApp Integration
function initTelegramData() {
    if (!tg) return;
    
    tg.ready();
    tg.expand();
    
    // Set theme colors if supported
    if (tg.themeParams) {
        document.documentElement.style.setProperty('--bg-primary', tg.themeParams.bg_color || '#0b0f19');
        document.documentElement.style.setProperty('--bg-secondary', tg.themeParams.secondary_bg_color || '#141c2f');
        document.documentElement.style.setProperty('--text-primary', tg.themeParams.text_color || '#ffffff');
        document.documentElement.style.setProperty('--text-secondary', tg.themeParams.hint_color || '#94a3b8');
    }
    
    // Extract user info
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        const tgUser = tg.initDataUnsafe.user;
        state.user.id = tgUser.id;
        state.user.first_name = tgUser.first_name || "Foydalanuvchi";
        state.user.username = tgUser.username ? `@${tgUser.username}` : "";
        
        // Formulate a profile initials avatar as backup or use photo_url if provided
        state.user.photo_url = tgUser.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(state.user.first_name)}&background=1e293b&color=ffffff&size=128`;
    }
}

// 2. Navigation
function switchTab(tabId) {
    // Hide all tabs
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".nav-tab-btn").forEach(el => el.classList.remove("active"));
    
    // Show selected tab
    const tabEl = document.getElementById(`tab-${tabId}`);
    if (tabEl) tabEl.classList.add("active");
    
    // Find active nav button
    const btnIdx = ['home', 'balance', 'history', 'profile'].indexOf(tabId);
    if (btnIdx !== -1) {
        document.querySelectorAll(".nav-tab-btn")[btnIdx].classList.add("active");
    }
    
    // If switching to history tab, refresh history
    if (tabId === 'history') {
        fetchHistory();
    }
    // If switching to balance or profile, refresh user details
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

// Scroll from banner to categories
function scrollToCatalog(category) {
    // Switch to home tab first if not already there
    switchTab('home');
    setTimeout(() => {
        const titleText = category === 'stars' ? '🌟 TELEGRAM STARS' : '💎 TELEGRAM PREMIUM';
        const sectionTitles = Array.from(document.querySelectorAll('.section-title'));
        const targetTitle = sectionTitles.find(el => el.textContent.includes(titleText));
        if (targetTitle) {
            targetTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

// Banner Carousel animation
let currentSlide = 0;
function startCarousel() {
    const slides = document.querySelectorAll(".carousel-slide");
    if (slides.length <= 1) return;
    
    setInterval(() => {
        slides[currentSlide].classList.remove("active");
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.add("active");
    }, 5000);
}

// 3. UI Rendering Helpers
function renderProfile() {
    // Top header profile info
    if (els.userAvatar) els.userAvatar.src = state.user.photo_url;
    if (els.profileAvatar) els.profileAvatar.src = state.user.photo_url;
    if (els.userDisplayName) els.userDisplayName.innerHTML = `${state.user.first_name} <span class="shark-emoji">🦈</span>`;
    
    // Profile Tab details
    if (els.profileName) els.profileName.textContent = state.user.first_name;
    if (els.profileUsername) els.profileUsername.textContent = state.user.username ? state.user.username : `ID: ${state.user.id}`;
    if (els.profileId) els.profileId.textContent = `ID: ${state.user.id}`;
    
    // Balances
    updateBalancesUI();
    
    // Stats & Links
    if (els.statsOrders) els.statsOrders.textContent = state.user.completed_orders;
    if (els.statsRegDate) els.statsRegDate.textContent = state.user.reg_date;
    
    if (els.linkNews) els.linkNews.href = state.settings.newsLink;
    if (els.linkSupport) els.linkSupport.href = state.settings.supportLink;
    
    if (els.cardNumber) els.cardNumber.textContent = state.settings.cardNumber;
    if (els.cardOwner) els.cardOwner.textContent = state.settings.cardOwner;
}

function updateBalancesUI() {
    const formattedBalance = `${state.user.balance.toLocaleString('uz-UZ')} UZS`;
    if (els.headerBalance) els.headerBalance.textContent = formattedBalance;
    if (els.mainBalance) els.mainBalance.textContent = formattedBalance;
    if (els.depositBalance) els.depositBalance.textContent = formattedBalance;
}

function renderCatalog() {
    if (!els.starsCatalog || !els.premiumCatalog) return;
    
    const stars = state.packages.filter(p => p.category === 'stars');
    const premium = state.packages.filter(p => p.category === 'premium');
    
    // Render Stars
    if (stars.length === 0) {
        els.starsCatalog.innerHTML = '<div class="loading-placeholder">Stars paketlar topilmadi.</div>';
    } else {
        els.starsCatalog.innerHTML = stars.map(p => `
            <div class="catalog-card">
                <div class="catalog-card-icon">🌟</div>
                <div class="catalog-card-name">${p.name}</div>
                <div class="catalog-card-price">${p.price.toLocaleString('uz-UZ')} UZS</div>
                <button class="btn-buy" onclick="openBuyModal(${p.id})">Sotib olish</button>
            </div>
        `).join('');
    }
    
    // Render Premium
    if (premium.length === 0) {
        els.premiumCatalog.innerHTML = '<div class="loading-placeholder">Premium paketlar topilmadi.</div>';
    } else {
        els.premiumCatalog.innerHTML = premium.map(p => `
            <div class="catalog-card">
                <div class="catalog-card-icon">💎</div>
                <div class="catalog-card-name">${p.name}</div>
                <div class="catalog-card-price">${p.price.toLocaleString('uz-UZ')} UZS</div>
                <button class="btn-buy" onclick="openBuyModal(${p.id})">Sotib olish</button>
            </div>
        `).join('');
    }
}

// 4. API Requests
async function fetchUserData() {
    try {
        const response = await fetch(`/api/user?user_id=${state.user.id}`);
        if (response.ok) {
            const data = await response.json();
            state.user.balance = data.balance;
            state.user.completed_orders = data.completed_orders;
            state.user.reg_date = data.joined_at_formatted || state.user.reg_date;
            if (data.settings) {
                state.settings.cardNumber = data.settings.card_number || state.settings.cardNumber;
                state.settings.cardOwner = data.settings.card_owner || state.settings.cardOwner;
                state.settings.newsLink = data.settings.news_link || state.settings.newsLink;
                state.settings.supportLink = data.settings.support_link || state.settings.supportLink;
            }
            renderProfile();
        }
    } catch (err) {
        console.error("Error fetching user data:", err);
    }
}

async function fetchCatalog() {
    try {
        const response = await fetch('/api/packages');
        if (response.ok) {
            state.packages = await response.json();
            renderCatalog();
        }
    } catch (err) {
        console.error("Error fetching catalog:", err);
        // Fallback to offline defaults if API fails
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
        const response = await fetch(`/api/history?user_id=${state.user.id}`);
        if (response.ok) {
            const data = await response.json();
            state.history.orders = data.orders || [];
            state.history.deposits = data.deposits || [];
            renderHistoryLists();
        }
    } catch (err) {
        console.error("Error fetching history:", err);
        renderHistoryLists(); // Renders empty state
    }
}

function renderHistoryLists() {
    const ordersContainer = document.getElementById("history-orders-container");
    const depositsContainer = document.getElementById("history-deposits-container");
    
    // Render Orders
    if (state.history.orders.length === 0) {
        ordersContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon-box"><i data-lucide="package"></i></div>
                <h3>Buyurtmalar hali yo'q</h3>
                <p>Buyurtmalar tarixingiz birinchi xaridingizdan keyin shu yerda ko'rinadi.</p>
            </div>
        `;
    } else {
        ordersContainer.innerHTML = state.history.orders.map(o => {
            let statusText = "Kutilmoqda";
            let statusClass = "status-pending";
            if (o.status === 'completed') {
                statusText = "Bajarildi";
                statusClass = "status-completed";
            } else if (o.status === 'cancelled') {
                statusText = "Rad etildi";
                statusClass = "status-cancelled";
            }
            
            return `
                <div class="history-card" data-search="${o.package_name.toLowerCase()} ${o.target_username.toLowerCase()}">
                    <div class="hc-left">
                        <span class="hc-title">${o.package_name}</span>
                        <span class="hc-target">Kimga: ${o.target_username}</span>
                        <span class="hc-date">${formatDate(o.created_at)}</span>
                    </div>
                    <div class="hc-right">
                        <span class="hc-price">${o.price.toLocaleString('uz-UZ')} UZS</span>
                        <span class="hc-status ${statusClass}">${statusText}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Render Deposits
    if (state.history.deposits.length === 0) {
        depositsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon-box"><i data-lucide="receipt"></i></div>
                <h3>Tranzaksiyalar mavjud emas</h3>
                <p>Tranzaksiya tarixingiz shu yerda ko'rinadi.</p>
            </div>
        `;
    } else {
        depositsContainer.innerHTML = state.history.deposits.map(d => {
            let statusText = "Kutilmoqda";
            let statusClass = "status-pending";
            if (d.status === 'approved') {
                statusText = "Tasdiqlandi";
                statusClass = "status-success";
            } else if (d.status === 'rejected') {
                statusText = "Rad etildi";
                statusClass = "status-rejected";
            }
            
            return `
                <div class="history-card" data-search="${d.payment_method.toLowerCase()}">
                    <div class="hc-left">
                        <span class="hc-title">Balansni to'ldirish</span>
                        <span class="hc-target">Turi: ${d.payment_method.toUpperCase()}</span>
                        <span class="hc-date">${formatDate(d.created_at)}</span>
                    </div>
                    <div class="hc-right">
                        <span class="hc-price">+${d.amount.toLocaleString('uz-UZ')} UZS</span>
                        <span class="hc-status ${statusClass}">${statusText}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (file.size > 10 * 1024 * 1024) {
        showToast("Rasm hajmi juda katta! Maksimal 10MB bo'lishi kerak.");
        event.target.value = '';
        return;
    }
    
    state.receiptFileName = file.name;
    document.getElementById("upload-status-text").textContent = `Tanlandi: ${file.name}`;
    
    // Read file as Base64 for upload
    const reader = new FileReader();
    reader.onload = function(e) {
        state.receiptBase64 = e.target.result;
        
        // Show preview image
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
    }).catch(err => {
        // Fallback for some webview containers
        const textArea = document.createElement("textarea");
        textArea.value = cardNum;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast("Karta raqami nusxalandi!");
        } catch (err2) {
            console.error("Could not copy card number: ", err2);
        }
        document.body.removeChild(textArea);
    });
}

async function submitDeposit() {
    const amountInput = document.getElementById("deposit-amount");
    const amount = parseFloat(amountInput.value);
    
    if (isNaN(amount) || amount < 5000) {
        showToast("Iltimos, kamida 5,000 UZS kiriting!");
        return;
    }
    
    if (!state.receiptBase64) {
        showToast("Iltimos, to'lov chekini yuklang!");
        return;
    }
    
    const submitBtn = document.getElementById("btn-submit-deposit");
    submitBtn.disabled = true;
    submitBtn.textContent = "Yuborilmoqda...";
    
    try {
        const response = await fetch('/api/deposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.user.id,
                amount: amount,
                payment_method: 'manual',
                receipt_base64: state.receiptBase64,
                file_name: state.receiptFileName
            })
        });
        
        if (response.ok) {
            showToast("To'lov tekshirishga yuborildi! Admin tasdiqlagach balansga tushadi ✅");
            
            // Reset deposit form
            amountInput.value = '';
            state.receiptBase64 = null;
            state.receiptFileName = null;
            document.getElementById("receipt-preview").style.display = "none";
            document.getElementById("upload-trigger").style.display = "flex";
            document.getElementById("upload-status-text").textContent = "Chek rasmini tanlang";
            document.getElementById("receipt-file").value = '';
            
            // Switch to History tab
            switchTab('history');
            switchHistorySubTab('deposits');
        } else {
            const errData = await response.json();
            showToast(errData.detail || "Xatolik yuz berdi!");
        }
    } catch (err) {
        console.error("Deposit submission error:", err);
        showToast("Server bilan bog'lanishda xatolik!");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i data-lucide="send"></i> To'lovni tekshirishga yuborish`;
        if (window.lucide) window.lucide.createIcons();
    }
}

// 6. Xarid qilish (Purchase) logic
function openBuyModal(packageId) {
    const pkg = state.packages.find(p => p.id === packageId);
    if (!pkg) return;
    
    state.selectedPackage = pkg;
    
    // Update Modal Details
    document.getElementById("modal-prod-icon").textContent = pkg.category === 'stars' ? '🌟' : '💎';
    document.getElementById("modal-prod-name").textContent = pkg.name;
    document.getElementById("modal-prod-price").textContent = `${pkg.price.toLocaleString('uz-UZ')} UZS`;
    
    // Balance check
    const balanceText = document.getElementById("modal-user-balance");
    const balanceStatus = document.getElementById("modal-balance-status");
    const confirmBtn = document.getElementById("btn-confirm-purchase");
    
    balanceText.textContent = `Mening balansim: ${state.user.balance.toLocaleString('uz-UZ')} UZS`;
    
    if (state.user.balance >= pkg.price) {
        balanceStatus.textContent = "Etarli";
        balanceStatus.className = "wpc-status status-success";
        confirmBtn.disabled = false;
        confirmBtn.textContent = "Xaridni tasdiqlash";
    } else {
        balanceStatus.textContent = "Etarli emas";
        balanceStatus.className = "wpc-status status-rejected";
        confirmBtn.disabled = true;
        confirmBtn.textContent = "Mablag' yetarli emas";
    }
    
    // Open Modal
    els.buyModal.classList.add("active");
}

function closeBuyModal() {
    els.buyModal.classList.remove("active");
    document.getElementById("order-target").value = '';
    state.selectedPackage = null;
}

async function confirmPurchase() {
    const targetInput = document.getElementById("order-target");
    const target = targetInput.value.trim();
    const pkg = state.selectedPackage;
    
    if (!pkg) return;
    
    if (!target) {
        showToast("Iltimos, Telegram username yoki telefon raqam kiriting!");
        return;
    }
    
    if (state.user.balance < pkg.price) {
        showToast("Balansda mablag' yetarli emas!");
        return;
    }
    
    const confirmBtn = document.getElementById("btn-confirm-purchase");
    confirmBtn.disabled = true;
    confirmBtn.textContent = "Yuborilmoqda...";
    
    try {
        const response = await fetch('/api/purchase', {
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
        
        if (response.ok) {
            const data = await response.json();
            // Deduct locally first
            state.user.balance = data.new_balance;
            updateBalancesUI();
            
            showToast("Buyurtma qabul qilindi va tekshirilmoqda! 🚀");
            closeBuyModal();
            
            // Switch to History tab
            switchTab('history');
            switchHistorySubTab('orders');
        } else {
            const errData = await response.json();
            showToast(errData.detail || "Xatolik yuz berdi!");
        }
    } catch (err) {
        console.error("Purchase error:", err);
        showToast("Server bilan bog'lanishda xatolik!");
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = "Xaridni tasdiqlash";
    }
}

// 7. Search/Filtering history
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

// 8. Helper Functions
function showToast(message) {
    if (!els.toast) return;
    
    document.getElementById("toast-message").textContent = message;
    els.toast.classList.add("active");
    
    setTimeout(() => {
        els.toast.classList.remove("active");
    }, 3000);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        // Handle SQLite timestamp string (YYYY-MM-DD HH:MM:SS) or ISO
        const d = new Date(dateStr.replace(' ', 'T'));
        if (isNaN(d.getTime())) return dateStr;
        return `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth()+1).toString().padStart(2, '0')}.${d.getFullYear()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    } catch (e) {
        return dateStr;
    }
}
