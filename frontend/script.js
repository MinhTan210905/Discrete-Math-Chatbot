const MAX_HISTORY_ITEMS = 8;
const HISTORY_API_URL = "http://localhost:3001/api/history";
let activeMenuId = null;
let isArchiveView = false;
let activeConversationId = null;
let historyCache = [];
let hasShownServerWarning = false;
let menuAnchorRect = null;

function getHistoryList() {
    return document.getElementById("chat-history");
}

function getChatBox() {
    return document.getElementById("chat-box");
}

function getFloatingMenu() {
    let menu = document.getElementById("history-floating-menu");
    if (menu) return menu;

    menu = document.createElement("div");
    menu.id = "history-floating-menu";
    menu.className = "history-floating-menu";
    menu.style.display = "none";
    document.body.appendChild(menu);
    return menu;
}

function uid() {
    return `${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

function normalizeItem(item) {
    if (typeof item === "string") {
        return {
            id: uid(),
            title: item,
            pinned: false,
            archived: false,
            group: false,
            createdAt: Date.now(),
            updatedAt: Date.now(),
            messages: [
                { role: "user", text: item },
                { role: "bot", text: "Đang trả lời..." }
            ]
        };
    }

    const safeMessages = Array.isArray(item.messages)
        ? item.messages
            .filter(function (message) {
                return message && (message.role === "user" || message.role === "bot") && typeof message.text === "string";
            })
            .map(function (message) {
                return {
                    role: message.role,
                    text: message.text
                };
            })
        : [];

    return {
        id: item.id || uid(),
        title: item.title || "Đoạn chat chưa đặt tên",
        pinned: Boolean(item.pinned),
        archived: Boolean(item.archived),
        group: Boolean(item.group),
        createdAt: item.createdAt || Date.now(),
        updatedAt: item.updatedAt || Date.now(),
        messages: safeMessages
    };
}

function loadHistory() {
    return historyCache.map(function (item) {
        return normalizeItem(item);
    });
}

function saveHistory(historyItems) {
    historyCache = historyItems.map(function (item) {
        return normalizeItem(item);
    });
    persistHistoryToServer(historyCache);
}

async function loadHistoryFromServer() {
    try {
        const response = await fetch(HISTORY_API_URL);
        if (!response.ok) {
            throw new Error("Không đọc được dữ liệu lịch sử từ server");
        }

        const data = await response.json();
        if (!Array.isArray(data)) {
            historyCache = [];
            return;
        }

        historyCache = data.map(function (item) {
            return normalizeItem(item);
        });
    } catch (error) {
        historyCache = [];
        if (!hasShownServerWarning) {
            alert("Chưa kết nối được server lưu lịch sử. Hãy chạy backend trước nhé.");
            hasShownServerWarning = true;
        }
    }
}

async function persistHistoryToServer(historyItems) {
    try {
        await fetch(HISTORY_API_URL, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(historyItems)
        });
    } catch (error) {
        if (!hasShownServerWarning) {
            alert("Không lưu được lịch sử lên server. Kiểm tra backend giúp mình nhé.");
            hasShownServerWarning = true;
        }
    }
}

function trimHistory(historyItems) {
    return historyItems.slice(0, MAX_HISTORY_ITEMS);
}

function sortHistory(historyItems) {
    return [...historyItems].sort(function (a, b) {
        if (a.pinned !== b.pinned) {
            return a.pinned ? -1 : 1;
        }
        return b.updatedAt - a.updatedAt;
    });
}

function updateHistoryById(id, updateFn) {
    const historyItems = loadHistory();
    const updatedItems = historyItems.map(function (item) {
        if (item.id !== id) return item;

        const newItem = updateFn({ ...item });
        return {
            ...newItem,
            updatedAt: Date.now()
        };
    });

    saveHistory(updatedItems);
    activeMenuId = null;
    renderHistory();
}

function removeHistoryById(id) {
    const historyItems = loadHistory().filter(function (item) {
        return item.id !== id;
    });

    saveHistory(historyItems);
    activeMenuId = null;
    renderHistory();
}

async function shareHistory(item) {
    try {
        const transcript = item.messages.length > 0
            ? item.messages
                .map(function (message) {
                    const label = message.role === "user" ? "Bạn" : "Trợ lý";
                    return `${label}: ${message.text}`;
                })
                .join("\n")
            : item.title;

        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(transcript);
            alert("Đã sao chép nội dung chia sẻ.");
        } else {
            alert("Trình duyệt chưa hỗ trợ sao chép tự động.");
        }
    } catch (error) {
        alert("Không thể chia sẻ lúc này, thử lại nhé.");
    }
}

function applyHistoryAction(action, item) {
    if (action === "share") {
        shareHistory(item);
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "group") {
        updateHistoryById(item.id, function (current) {
            return {
                ...current,
                group: true,
                title: current.title.startsWith("[Nhóm]") ? current.title : `[Nhóm] ${current.title}`
            };
        });
        return;
    }

    if (action === "rename") {
        const newName = prompt("Nhập tên mới cho đoạn chat:", item.title);
        if (!newName || !newName.trim()) {
            activeMenuId = null;
            renderHistory();
            return;
        }
        updateHistoryById(item.id, function (current) {
            return {
                ...current,
                title: newName.trim()
            };
        });
        return;
    }

    if (action === "pin") {
        updateHistoryById(item.id, function (current) {
            return {
                ...current,
                pinned: !current.pinned
            };
        });
        return;
    }

    if (action === "archive") {
        updateHistoryById(item.id, function (current) {
            return {
                ...current,
                archived: true
            };
        });
        return;
    }

    if (action === "unarchive") {
        updateHistoryById(item.id, function (current) {
            return {
                ...current,
                archived: false
            };
        });
        return;
    }

    if (action === "delete") {
        const isConfirmed = confirm("Xóa đoạn chat này khỏi lịch sử?");
        if (isConfirmed) {
            removeHistoryById(item.id);
        } else {
            activeMenuId = null;
            renderHistory();
        }
    }
}

function createActionButton(label, action, item, extraClass) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = extraClass ? `history-action ${extraClass}` : "history-action";
    button.textContent = label;
    button.addEventListener("click", function (event) {
        event.stopPropagation();
        applyHistoryAction(action, item);
    });
    return button;
}

function renderFloatingMenu(item) {
    const menu = getFloatingMenu();

    if (!item || !menuAnchorRect) {
        menu.innerHTML = "";
        menu.style.display = "none";
        return;
    }

    menu.innerHTML = "";
    menu.appendChild(createActionButton("Chia sẻ", "share", item));
    menu.appendChild(createActionButton("Bắt đầu đoạn chat nhóm", "group", item));
    menu.appendChild(createActionButton("Đổi tên", "rename", item));
    menu.appendChild(createActionButton(item.pinned ? "Bỏ ghim" : "Ghim đoạn chat", "pin", item));
    menu.appendChild(createActionButton(isArchiveView ? "Bỏ lưu trữ" : "Lưu trữ", isArchiveView ? "unarchive" : "archive", item));
    menu.appendChild(createActionButton("Xóa", "delete", item, "delete"));

    const menuWidth = 230;
    const menuHeight = 280;
    const left = Math.min(window.innerWidth - menuWidth - 12, menuAnchorRect.right + 10);
    const top = Math.min(window.innerHeight - menuHeight - 12, menuAnchorRect.top - 4);

    menu.style.left = `${Math.max(12, left)}px`;
    menu.style.top = `${Math.max(12, top)}px`;
    menu.style.display = "block";
}

function renderHistory() {
    const historyList = getHistoryList();
    if (!historyList) return;

    const historyItems = sortHistory(loadHistory());
    const visibleItems = historyItems.filter(function (item) {
        return isArchiveView ? item.archived : !item.archived;
    });

    historyList.innerHTML = "";

    if (visibleItems.length === 0) {
        renderFloatingMenu(null);
        const emptyItem = document.createElement("li");
        emptyItem.className = "history-empty";
        emptyItem.textContent = isArchiveView
            ? "Kho lưu trữ đang trống"
            : "Chưa có cuộc trò chuyện nào";
        historyList.appendChild(emptyItem);
        return;
    }

    visibleItems.forEach(function (item) {
        const listItem = document.createElement("li");
        const row = document.createElement("div");
        row.className = "history-row";

        const title = document.createElement("span");
        title.className = "history-title";

        let prefix = "";
        if (item.pinned) prefix += "📌 ";
        if (item.group) prefix += "👥 ";
        title.textContent = `${prefix}${item.title}`;

        const menuBtn = document.createElement("button");
        menuBtn.type = "button";
        menuBtn.className = "history-menu-btn";
        menuBtn.textContent = "⋯";
        menuBtn.title = "Tùy chọn";

        menuBtn.addEventListener("click", function (event) {
            event.stopPropagation();
            if (activeMenuId === item.id) {
                activeMenuId = null;
                menuAnchorRect = null;
            } else {
                activeMenuId = item.id;
                menuAnchorRect = menuBtn.getBoundingClientRect();
            }
            renderHistory();
        });

        title.addEventListener("click", function () {
            activeConversationId = item.id;
            activeMenuId = null;
            renderHistory();
            renderConversation(item.id);

            const input = document.getElementById("user-input");
            if (input) input.focus();
        });

        row.appendChild(title);
        row.appendChild(menuBtn);
        listItem.appendChild(row);

        if (activeConversationId === item.id) {
            listItem.classList.add("active");
        }

        historyList.appendChild(listItem);
    });

    const activeItem = visibleItems.find(function (item) {
        return item.id === activeMenuId;
    });
    renderFloatingMenu(activeItem || null);
}

function createMessageNode(role, text) {
    const messageNode = document.createElement("div");
    messageNode.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    messageNode.appendChild(bubble);
    return messageNode;
}

function renderWelcomeMessage() {
    const chatBox = getChatBox();
    if (!chatBox) return;

    chatBox.innerHTML = "";
    chatBox.appendChild(
        createMessageNode(
            "bot",
            "Xin chào 👋 Mình là Trợ lý AI CNTT. Bạn cứ hỏi bất kỳ nội dung Toán Rời Rạc nào nhé!"
        )
    );
}

function renderConversation(conversationId) {
    const chatBox = getChatBox();
    if (!chatBox) return;

    const historyItems = loadHistory();
    const conversation = historyItems.find(function (item) {
        return item.id === conversationId;
    });

    chatBox.innerHTML = "";

    if (!conversation || !conversation.messages || conversation.messages.length === 0) {
        renderWelcomeMessage();
        return;
    }

    conversation.messages.forEach(function (message) {
        chatBox.appendChild(createMessageNode(message.role, message.text));
    });

    chatBox.scrollTop = chatBox.scrollHeight;
}

function saveConversationMessage(messageText) {
    const historyItems = loadHistory();
    const title = messageText.length > 60 ? `${messageText.slice(0, 60)}...` : messageText;
    const now = Date.now();

    let currentConversation = historyItems.find(function (item) {
        return item.id === activeConversationId;
    });

    if (!currentConversation) {
        currentConversation = {
            id: uid(),
            title,
            pinned: false,
            archived: false,
            group: false,
            createdAt: now,
            updatedAt: now,
            messages: []
        };
        activeConversationId = currentConversation.id;
        historyItems.unshift(currentConversation);
    }

    if (currentConversation.messages.length === 0) {
        currentConversation.title = title;
    }

    currentConversation.messages.push({ role: "user", text: messageText });
    currentConversation.messages.push({ role: "bot", text: "Đang trả lời..." });
    currentConversation.updatedAt = now;

    const sorted = sortHistory(historyItems);
    saveHistory(trimHistory(sorted));
    renderHistory();
}

function resetChat() {
    activeConversationId = null;
    renderWelcomeMessage();
    renderHistory();

    const input = document.getElementById("user-input");
    if (input) {
        input.value = "";
        input.focus();
    }
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    const chatBox = getChatBox();

    if (message === "" || !chatBox) return;

    chatBox.appendChild(createMessageNode("user", message));
    chatBox.appendChild(createMessageNode("bot", "Đang trả lời..."));

    chatBox.scrollTop = chatBox.scrollHeight;
    saveConversationMessage(message);
    input.value = "";
}

const userInput = document.getElementById("user-input");
if (userInput) {
    userInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
}

const newChatBtn = document.querySelector(".new-chat-btn");
if (newChatBtn) {
    newChatBtn.addEventListener("click", resetChat);
}

document.querySelectorAll(".filter-btn").forEach(function (button) {
    button.addEventListener("click", function () {
        document.querySelectorAll(".filter-btn").forEach(function (node) {
            node.classList.remove("active");
        });
        button.classList.add("active");
        isArchiveView = button.dataset.view === "archived";
        activeMenuId = null;
        renderHistory();
    });
});

document.addEventListener("click", function (event) {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const clickedMenu = target.closest(".history-floating-menu");
    const clickedMenuButton = target.closest(".history-menu-btn");

    if (!clickedMenu && !clickedMenuButton && activeMenuId !== null) {
        activeMenuId = null;
        menuAnchorRect = null;
        renderHistory();
    }
});

window.addEventListener("resize", function () {
    if (activeMenuId !== null) {
        activeMenuId = null;
        menuAnchorRect = null;
        renderHistory();
    }
});

async function initApp() {
    await loadHistoryFromServer();

    const firstConversation = sortHistory(loadHistory()).find(function (item) {
        return !item.archived;
    });

    if (firstConversation) {
        activeConversationId = firstConversation.id;
        renderConversation(firstConversation.id);
    } else {
        renderWelcomeMessage();
    }

    renderHistory();
}

initApp();