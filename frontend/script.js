const CONVERSATIONS_API_URL = "http://localhost:3001/api/conversations";
const CHAT_API_URL = "http://localhost:3001/api/chat";
const MIN_THINKING_MS = 900;
const DISPLAY_REPLACEMENTS = [
    [//g, " or "],
    [/∨/g, " or "],
    [//g, " and "],
    [/∧/g, " and "],
    [//g, " not "],
    [/¬/g, " not "],
    [/→/g, " -> "],
    [/⇒/g, " -> "],
    [/↔/g, " <-> "],
    [/⇔/g, " <-> "],
    [/∪/g, " union "],
    [/∩/g, " intersection "],
    [/⊆/g, " subseteq "],
    [/⊂/g, " subset "],
    [/⊇/g, " superseteq "],
    [/⊃/g, " superset "],
    [/∈/g, " in "],
    [/∉/g, " not in "],
];
let activeMenuId = null;
let isArchiveView = false;
let activeConversationId = null;
let conversations = [];
let activeMessages = [];
let hasShownServerWarning = false;
let menuAnchorRect = null;
let sendingInProgress = false;

function sanitizeDisplayText(text) {
    let output = String(text || "");
    DISPLAY_REPLACEMENTS.forEach(([pattern, replacement]) => {
        output = output.replace(pattern, replacement);
    });
    return output
        .replace(/\r/g, "")
        .replace(/[ \t]+\n/g, "\n")
        .replace(/\n{3,}/g, "\n\n")
        .replace(/[ \t]{2,}/g, " ")
        .trim();
}

function getHistoryList() {
    return document.getElementById("chat-history");
}

function getChatBox() {
    return document.getElementById("chat-box");
}

function getInput() {
    return document.getElementById("user-input");
}

function getSendButton() {
    return document.getElementById("send-button");
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

async function apiFetch(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const fallback = { message: "Request failed" };
        let payload = fallback;
        try {
            payload = await response.json();
        } catch (error) {
            payload = fallback;
        }
        throw new Error(payload.message || "Request failed");
    }
    return response.json();
}

function mapRoleToClass(role) {
    return role === "assistant" ? "bot" : "user";
}

function createMessageNode(message, options) {
    const messageNode = document.createElement("div");
    const roleClass = mapRoleToClass(message.role);
    messageNode.className = `message ${roleClass}`;
    if (options && options.pending) {
        messageNode.classList.add("pending");
    }

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = sanitizeDisplayText(message.text);
    messageNode.appendChild(bubble);

    return messageNode;
}

function scrollChatToBottom() {
    const chatBox = getChatBox();
    if (!chatBox) return;
    chatBox.scrollTop = chatBox.scrollHeight;
}

function renderWelcomeMessage() {
    const chatBox = getChatBox();
    if (!chatBox) return;

    chatBox.innerHTML = "";
    chatBox.appendChild(
        createMessageNode({
            role: "assistant",
            text: "Xin chào! Mình là trợ lý Toán rời rạc. Bạn cứ chào hỏi bình thường, hoặc hỏi lý thuyết và bài tập mình sẽ hỗ trợ từng bước nhé.",
        })
    );
}

function renderConversationMessages(messages) {
    const chatBox = getChatBox();
    if (!chatBox) return;

    chatBox.innerHTML = "";
    if (!Array.isArray(messages) || messages.length === 0) {
        renderWelcomeMessage();
        return;
    }

    messages.forEach(message => {
        chatBox.appendChild(createMessageNode(message));
    });

    scrollChatToBottom();
}

function sortConversations(items) {
    return [...items].sort(function (left, right) {
        if (left.pinned !== right.pinned) {
            return left.pinned ? -1 : 1;
        }
        return right.updatedAt - left.updatedAt;
    });
}

async function loadConversations() {
    const data = await apiFetch(CONVERSATIONS_API_URL);
    conversations = Array.isArray(data) ? data : [];
    renderHistory();
    return conversations;
}

async function loadConversation(conversationId) {
    if (!conversationId) {
        activeConversationId = null;
        activeMessages = [];
        renderWelcomeMessage();
        renderHistory();
        return null;
    }

    const payload = await apiFetch(`${CONVERSATIONS_API_URL}/${conversationId}/messages`);
    activeConversationId = payload.conversation.id;
    activeMessages = Array.isArray(payload.messages) ? payload.messages : [];
    renderConversationMessages(activeMessages);
    renderHistory();
    return payload;
}

async function loadInitialConversation() {
    const sorted = sortConversations(conversations);
    const preferred = sorted.find(item => !item.archived) || sorted[0] || null;

    if (!preferred) {
        activeConversationId = null;
        activeMessages = [];
        renderWelcomeMessage();
        renderHistory();
        return;
    }

    await loadConversation(preferred.id);
}

function renderFloatingMenu(item) {
    const menu = getFloatingMenu();
    if (!item || !menuAnchorRect) {
        menu.innerHTML = "";
        menu.style.display = "none";
        return;
    }

    function createActionButton(label, action, extraClass) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = extraClass ? `history-action ${extraClass}` : "history-action";
        button.textContent = label;
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            applyHistoryAction(action, item).catch(function (error) {
                alert(error.message || "Không thể xử lý thao tác lịch sử lúc này.");
            });
        });
        return button;
    }

    menu.innerHTML = "";
    menu.appendChild(createActionButton("Chia sẻ", "share"));
    menu.appendChild(createActionButton("Đánh dấu nhóm", "group"));
    menu.appendChild(createActionButton("Đổi tên", "rename"));
    menu.appendChild(createActionButton(item.pinned ? "Bỏ ghim" : "Ghim đoạn chat", "pin"));
    menu.appendChild(createActionButton(isArchiveView ? "Bỏ lưu trữ" : "Lưu trữ", isArchiveView ? "unarchive" : "archive"));
    menu.appendChild(createActionButton("Xóa", "delete", "delete"));

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

    const visibleItems = sortConversations(conversations).filter(function (item) {
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
        if (item.pinned) prefix += "PIN ";
        if (item.grouped) prefix += "GROUP ";
        title.textContent = `${prefix}${item.title}`;

        const menuBtn = document.createElement("button");
        menuBtn.type = "button";
        menuBtn.className = "history-menu-btn";
        menuBtn.textContent = "...";
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
            activeMenuId = null;
            menuAnchorRect = null;
            loadConversation(item.id).catch(function (error) {
                alert(error.message || "Không tải được cuộc trò chuyện.");
            });
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

function resetChat() {
    activeConversationId = null;
    activeMessages = [];
    renderWelcomeMessage();
    renderHistory();
    const input = getInput();
    if (input) {
        input.value = "";
        input.focus();
    }
}

async function requestChatResponse(messageText) {
    const modelSelect = document.getElementById("model-select");
    const mode = modelSelect ? modelSelect.value : "traditional";

    return apiFetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            conversationId: activeConversationId,
            message: messageText,
            mode: mode,
        }),
    });
}

function updatePendingBubble(messageNode, text) {
    if (!messageNode) return;
    const bubble = messageNode.querySelector(".bubble");
    if (bubble) {
        bubble.textContent = sanitizeDisplayText(text);
    }
}

function sleep(ms) {
    return new Promise(function (resolve) {
        setTimeout(resolve, ms);
    });
}

function startThinkingAnimation(messageNode) {
    const bubble = messageNode ? messageNode.querySelector(".bubble") : null;
    if (!bubble) {
        return function () {};
    }
    messageNode.classList.add("thinking");

    const frames = ["Đang suy nghĩ.", "Đang suy nghĩ..", "Đang suy nghĩ..."];
    let frameIndex = 0;
    bubble.textContent = frames[frameIndex];

    const timerId = setInterval(function () {
        frameIndex = (frameIndex + 1) % frames.length;
        bubble.textContent = frames[frameIndex];
    }, 250);

    return function stopThinking() {
        clearInterval(timerId);
        messageNode.classList.remove("thinking");
    };
}

async function sendMessage() {
    if (sendingInProgress) return;

    const input = getInput();
    const chatBox = getChatBox();
    if (!input || !chatBox) return;

    const message = input.value.trim();
    if (!message) return;

    sendingInProgress = true;
    input.disabled = true;
    const sendButton = getSendButton();
    if (sendButton) sendButton.disabled = true;

    if (!activeConversationId && activeMessages.length === 0) {
        chatBox.innerHTML = "";
    }

    const userNode = createMessageNode({ role: "user", text: message });
    const pendingNode = createMessageNode({ role: "assistant", text: "Đang suy nghĩ..." }, { pending: true });

    chatBox.appendChild(userNode);
    chatBox.appendChild(pendingNode);
    scrollChatToBottom();
    input.value = "";

    const stopThinking = startThinkingAnimation(pendingNode);

    try {
        const responsePromise = requestChatResponse(message);
        await Promise.all([responsePromise, sleep(MIN_THINKING_MS)]);
        const payload = await responsePromise;

        stopThinking();
        updatePendingBubble(pendingNode, payload.reply);
        activeConversationId = payload.conversationId;
        await loadConversations();
        await loadConversation(payload.conversationId);
    } catch (error) {
        stopThinking();
        const fallbackReply = error.message || "Mình chưa kết nối được server trả lời. Bạn kiểm tra backend rồi thử lại nhé.";
        updatePendingBubble(pendingNode, fallbackReply);
        if (!hasShownServerWarning) {
            alert(fallbackReply);
            hasShownServerWarning = true;
        }
    } finally {
        sendingInProgress = false;
        input.disabled = false;
        if (sendButton) sendButton.disabled = false;
        input.focus();
    }
}

async function updateConversation(itemId, patch) {
    await apiFetch(`${CONVERSATIONS_API_URL}/${itemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
    });
    await loadConversations();
    if (activeConversationId === itemId) {
        await loadConversation(itemId);
    }
}

async function removeConversation(itemId) {
    await apiFetch(`${CONVERSATIONS_API_URL}/${itemId}`, {
        method: "DELETE",
    });

    const wasActive = activeConversationId === itemId;
    await loadConversations();

    if (wasActive) {
        const sorted = sortConversations(conversations);
        const nextConversation = sorted.find(item => !item.archived) || sorted[0] || null;
        if (nextConversation) {
            await loadConversation(nextConversation.id);
        } else {
            resetChat();
        }
    }
}

async function shareConversation(item) {
    const payload = await apiFetch(`${CONVERSATIONS_API_URL}/${item.id}/messages`);
    const transcript = payload.messages.length > 0
        ? payload.messages
            .map(function (message) {
                const label = message.role === "assistant" ? "Trợ lý" : "Bạn";
                return `${label}: ${sanitizeDisplayText(message.text)}`;
            })
            .join("\n")
        : item.title;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(transcript);
        alert("Đã sao chép nội dung chia sẻ.");
    } else {
        alert("Trình duyệt chưa hỗ trợ sao chép tự động.");
    }
}

async function applyHistoryAction(action, item) {
    if (action === "share") {
        await shareConversation(item);
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "group") {
        await updateConversation(item.id, { grouped: !item.grouped });
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "rename") {
        const newName = prompt("Nhập tên mới cho đoạn chat:", item.title);
        if (!newName || !newName.trim()) {
            activeMenuId = null;
            renderHistory();
            return;
        }
        await updateConversation(item.id, { title: newName.trim() });
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "pin") {
        await updateConversation(item.id, { pinned: !item.pinned });
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "archive") {
        await updateConversation(item.id, { archived: true });
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "unarchive") {
        await updateConversation(item.id, { archived: false });
        activeMenuId = null;
        renderHistory();
        return;
    }

    if (action === "delete") {
        const isConfirmed = confirm("Xóa đoạn chat này khỏi lịch sử?");
        if (!isConfirmed) {
            activeMenuId = null;
            renderHistory();
            return;
        }
        await removeConversation(item.id);
        activeMenuId = null;
        renderHistory();
    }
}

const userInput = getInput();
if (userInput) {
    userInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
}

const sendButton = getSendButton();
if (sendButton) {
    sendButton.addEventListener("click", sendMessage);
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
    try {
        await loadConversations();
        await loadInitialConversation();
    } catch (error) {
        conversations = [];
        activeConversationId = null;
        activeMessages = [];
        renderWelcomeMessage();
        renderHistory();
        if (!hasShownServerWarning) {
            alert("Chưa kết nối được server chat. Hãy chạy backend trước nhé.");
            hasShownServerWarning = true;
        }
    }
}

initApp();
window.sendMessage = sendMessage;
