/* =====================================================
   DASHBOARD
   ===================================================== */

async function loadDashboard() {
    try {
        const response = await fetch("/dashboard");

        if (!response.ok) {
            throw new Error("Dashboard request failed");
        }

        const data = await response.json();

        const unitsSold = document.getElementById("unitsSold");
        const revenue = document.getElementById("revenue");
        const criticalStock = document.getElementById("criticalStock");
        const salesSpikes = document.getElementById("salesSpikes");

        if (unitsSold) {
            unitsSold.textContent = Number(data.units_sold || 0).toLocaleString();
        }

        if (revenue) {
            revenue.textContent = data.revenue ?? "—";
        }

        if (criticalStock) {
            criticalStock.textContent = data.critical_stock ?? "—";
        }

        if (salesSpikes) {
            salesSpikes.textContent = data.sales_spikes ?? "—";
        }

    } catch (error) {
        console.error("Dashboard error:", error);
    }
}


/* =====================================================
   RESULT CARD RENDERING
   ===================================================== */

/*
 * Backend priority labels -> visual priority class.
 * Anything not listed here falls back to "normal".
 */
const PRIORITY_CLASS = {
    "CRITICAL": "critical",
    "CRIT": "critical",
    "HIGH": "high",
    "MEDIUM": "high",
    "LOW": "low",
    "NORMAL": "normal",
    "TOP SELLER": "normal",
    "STORE": "normal",
    "PRODUCT": "normal"
};

/* Short badge text shown on each card. */
const PRIORITY_LABEL = {
    "CRITICAL": "CRIT",
    "HIGH": "HIGH",
    "MEDIUM": "MED",
    "LOW": "LOW",
    "NORMAL": "OK",
    "TOP SELLER": "TOP",
    "STORE": "STORE",
    "PRODUCT": "ITEM"
};

const PRIORITY_ICON = {
    "critical": "⚠",
    "high": "▲",
    "low": "▼",
    "normal": "●"
};

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function initials(text) {
    if (!text) return "•";

    const words = String(text).trim().split(/\s+/).filter(Boolean);

    if (words.length === 0) return "•";
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase();

    return (words[0][0] + words[1][0]).toUpperCase();
}

/*
 * Builds the small "ID / store" subtitle line shown
 * under each card title, from whatever identifying
 * fields the backend included on that card.
 */
function buildSubtitle(card) {
    const parts = [];

    if (card.item_id) {
        parts.push(`ID: ${card.item_id}`);
    }

    if (card.store_id && !String(card.title || "").includes(card.store_id)) {
        parts.push(`Store: ${card.store_id}`);
    }

    return parts.join(" · ");
}

function renderCard(card) {
    const priorityKey = String(card.priority || "NORMAL").toUpperCase();
    const priorityClass = PRIORITY_CLASS[priorityKey] || "normal";
    const priorityLabel = PRIORITY_LABEL[priorityKey] || priorityKey;
    const priorityIcon = PRIORITY_ICON[priorityClass] || "●";

    const subtitle = buildSubtitle(card);

    const statusBlock = card.status
        ? `
            <div class="result-status">
                <div class="status-heading">
                    <span class="status-badge-dot"></span>
                    STATUS
                </div>
                <div class="status-text">${escapeHtml(card.status)}</div>
            </div>
        `
        : "";

    const actionBlock = card.action
        ? `
            <div class="result-action">
                <div class="action-heading">
                    <span>➜</span> RECOMMENDED ACTION
                </div>
                <div class="action-text">${escapeHtml(card.action)}</div>
            </div>
        `
        : "";

    return `
        <div class="result-card ${priorityClass}">
            <div class="card-priority-line"></div>

            <div class="result-card-top">
                <div class="product-info">
                    <div class="product-icon">${escapeHtml(initials(card.title))}</div>
                    <div class="result-title-wrap">
                        <div class="result-title">${escapeHtml(card.title || "Item")}</div>
                        ${subtitle ? `<div class="result-subtitle">${escapeHtml(subtitle)}</div>` : ""}
                    </div>
                </div>

                <span class="badge">
                    <span class="badge-icon">${priorityIcon}</span>
                    ${escapeHtml(priorityLabel)}
                </span>
            </div>

            ${card.main ? `<div class="result-main">${escapeHtml(card.main)}</div>` : ""}
            ${card.detail ? `<div class="result-detail">${escapeHtml(card.detail)}</div>` : ""}

            ${statusBlock}
            ${actionBlock}
        </div>
    `;
}

/* Friendly heading for the summary panel, based on intent. */
const INTENT_HEADING = {
    "stock_out": "Stock-out risk",
    "overstock": "Overstocked inventory",
    "sales_performance": "Top-selling products",
    "sales_trend": "Sales movement",
    "store_performance": "Store performance",
    "product_analysis": "Product overview",
    "general": "Analysis"
};

const INTENT_NOTE = {
    "stock_out": "These products are likely to run out of stock soon based on current inventory and average daily demand.",
    "overstock": "These products are moving slowly relative to current stock levels and may be tying up capital.",
    "sales_performance": "Ranked by total units sold across all stores in the available sales data.",
    "sales_trend": "Compares recent sales against the previous 7-day period for each product.",
    "store_performance": "Ranked by total revenue across the available sales data."
};

/*
 * Renders the full result payload from /ask: the manager
 * summary, the grid of per-item cards, or an empty state
 * when the intent expects items but none were found.
 */
function renderResults(data) {

    const responseContainer = document.getElementById("responseContainer");
    const summaryBox = document.getElementById("summaryBox");
    const summaryHeading = document.getElementById("summaryHeading");
    const summaryText = document.getElementById("summaryText");
    const results = document.getElementById("results");
    const emptyState = document.getElementById("emptyState");
    const emptyText = document.getElementById("emptyText");
    const noteBox = document.getElementById("noteBox");
    const noteText = document.getElementById("noteText");

    const intent = data.intent || "general";
    const cards = Array.isArray(data.cards) ? data.cards : [];
    const summary = (data.summary || data.answer || "").trim();

    /* Summary panel */
    if (summary && summaryBox && summaryText && summaryHeading) {
        summaryHeading.textContent = INTENT_HEADING[intent] || "Analysis";
        summaryText.textContent = summary;
        summaryBox.classList.remove("hidden");
    } else if (summaryBox) {
        summaryBox.classList.add("hidden");
    }

    /* Result cards */
    if (results) {
        if (cards.length > 0) {
            results.innerHTML = cards.map(renderCard).join("");
            results.classList.remove("hidden");
        } else {
            results.innerHTML = "";
            results.classList.add("hidden");
        }
    }

    /* Empty state (only for intents that normally return items) */
    const expectsItems = intent !== "general";

    if (emptyState) {
        if (cards.length === 0 && expectsItems) {
            if (emptyText) {
                emptyText.textContent =
                    "No items currently match this question based on the available data.";
            }
            emptyState.classList.remove("hidden");
        } else {
            emptyState.classList.add("hidden");
        }
    }

    /* Contextual note under the results */
    if (noteBox && noteText) {
        const note = INTENT_NOTE[intent];

        if (note && cards.length > 0) {
            noteText.textContent = note;
            noteBox.classList.remove("hidden");
        } else {
            noteBox.classList.add("hidden");
        }
    }

    if (responseContainer) {
        responseContainer.classList.remove("hidden");
    }
}


/* =====================================================
   ASK RETAILIQ
   ===================================================== */

async function askQuestion(question = null) {

    const questionInput = document.getElementById("question");
    const askButton = document.getElementById("askButton");
    const loading = document.getElementById("loading");
    const responseContainer = document.getElementById("responseContainer");
    const errorContainer = document.getElementById("errorContainer");
    const errorMessage = document.getElementById("errorMessage");

    if (!questionInput || !askButton) {
        console.error("RetailIQ: required elements not found.");
        return;
    }

    if (question !== null) {
        questionInput.value = question;
    }

    const userQuestion = questionInput.value.trim();

    if (!userQuestion) {
        questionInput.focus();
        return;
    }

    /* Reset previous states */
    if (responseContainer) {
        responseContainer.classList.add("hidden");
    }

    if (errorContainer) {
        errorContainer.classList.add("hidden");
    }

    /* Loading state */
    if (loading) {
        loading.classList.remove("hidden");
    }

    askButton.disabled = true;
    askButton.textContent = "Analyzing...";

    try {

        const result = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: userQuestion })
        });

        const data = await result.json();

        if (!result.ok) {
            throw new Error(data.error || "Unable to process your question.");
        }

        renderResults(data);

        if (responseContainer) {
            responseContainer.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }

    } catch (error) {

        console.error("RetailIQ error:", error);

        if (errorMessage) {
            errorMessage.textContent = error.message || "Unable to analyze the question.";
        }

        if (errorContainer) {
            errorContainer.classList.remove("hidden");
        }

    } finally {

        if (loading) {
            loading.classList.add("hidden");
        }

        askButton.disabled = false;
        askButton.innerHTML = '<span class="btn-icon">➤</span> Ask RetailIQ';
    }
}

function useQuestion(question) {
    askQuestion(question);
}


/* =====================================================
   SIDEBAR / NAVIGATION
   ===================================================== */

function setupSidebar() {

    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");

    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }

    /* Scroll-to-section nav items */
    document.querySelectorAll(".nav-item[data-scroll]").forEach(function (btn) {

        btn.addEventListener("click", function () {

            document.querySelectorAll(".nav-item").forEach(function (b) {
                b.classList.remove("active");
            });

            btn.classList.add("active");

            const targetId = btn.getAttribute("data-scroll");
            const target = document.getElementById(targetId);

            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }

            if (sidebar) {
                sidebar.classList.remove("open");
            }
        });
    });

    /* Quick question buttons */
    document.querySelectorAll(".quick-item[data-question]").forEach(function (btn) {

        btn.addEventListener("click", function () {

            const question = btn.getAttribute("data-question");

            document.querySelectorAll(".nav-item").forEach(function (b) {
                b.classList.remove("active");
            });

            const copilotNav = document.querySelector('.nav-item[data-scroll="copilot"]');

            if (copilotNav) {
                copilotNav.classList.add("active");
            }

            askQuestion(question);

            if (sidebar) {
                sidebar.classList.remove("open");
            }
        });
    });
}


/* =====================================================
   PAGE INITIALIZATION
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    loadDashboard();
    setupSidebar();

    const questionInput = document.getElementById("question");

    if (questionInput) {

        /* Auto-grow the textarea as the manager types */
        questionInput.addEventListener("input", function () {
            questionInput.style.height = "auto";
            questionInput.style.height = Math.min(questionInput.scrollHeight, 120) + "px";
        });

        questionInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && event.ctrlKey) {
                event.preventDefault();
                askQuestion();
            }
        });
    }

});
