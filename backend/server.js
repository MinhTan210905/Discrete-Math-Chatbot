require("dotenv").config();
const http = require("http");
const path = require("path");

const config = require("./config");
const { ChatService } = require("./chat-service");
const { ConversationRepository } = require("./conversation-repository");

function getCorsHeaders() {
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    };
}

function sendJson(response, statusCode, payload) {
    response.writeHead(statusCode, {
        "Content-Type": "application/json; charset=utf-8",
        ...getCorsHeaders(),
    });
    response.end(JSON.stringify(payload));
}

function readRequestBody(request) {
    return new Promise((resolve, reject) => {
        let body = "";
        request.on("data", chunk => {
            body += chunk;
        });
        request.on("end", () => resolve(body));
        request.on("error", reject);
    });
}

function createServices(options = {}) {
    const repository = options.repository || new ConversationRepository({
        dbPath: options.dbPath || config.DB_PATH,
        legacyHistoryPath: Object.prototype.hasOwnProperty.call(options, "legacyHistoryPath")
            ? options.legacyHistoryPath
            : path.join(config.DATA_DIR, "history-temp.json"),
    });

    return {
        repository,
        chatService: new ChatService({ repository }),
    };
}

function parseConversationPatch(payload) {
    return {
        title: typeof payload.title === "string" ? payload.title : undefined,
        pinned: typeof payload.pinned === "boolean" ? payload.pinned : undefined,
        archived: typeof payload.archived === "boolean" ? payload.archived : undefined,
        grouped:
            typeof payload.grouped === "boolean"
                ? payload.grouped
                : typeof payload.group === "boolean"
                    ? payload.group
                    : undefined,
    };
}

function createServer(options = {}) {
    const services = createServices(options);

    const server = http.createServer(async (request, response) => {
        try {
            if (request.method === "OPTIONS") {
                response.writeHead(204, getCorsHeaders());
                response.end();
                return;
            }

            const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
            const pathname = url.pathname;

            if (pathname === "/api/conversations" && request.method === "GET") {
                sendJson(response, 200, services.chatService.listConversations());
                return;
            }

            if (pathname === "/api/history" && request.method === "GET") {
                sendJson(response, 200, services.repository.listHistoryLegacyFormat());
                return;
            }

            if (pathname === "/api/history" && request.method === "PUT") {
                const body = await readRequestBody(request);
                const payload = JSON.parse(body || "[]");
                if (!Array.isArray(payload)) {
                    sendJson(response, 400, { message: "Dữ liệu lịch sử phải là mảng." });
                    return;
                }
                services.repository.mergeLegacyHistorySnapshot(payload);
                sendJson(response, 200, { ok: true });
                return;
            }

            const conversationMessagesMatch = pathname.match(/^\/api\/conversations\/([^/]+)\/messages$/);
            if (conversationMessagesMatch && request.method === "GET") {
                const result = services.chatService.getConversationMessages(conversationMessagesMatch[1]);
                if (!result) {
                    sendJson(response, 404, { message: "Không tìm thấy cuộc trò chuyện." });
                    return;
                }
                sendJson(response, 200, result);
                return;
            }

            const conversationMatch = pathname.match(/^\/api\/conversations\/([^/]+)$/);
            if (conversationMatch && request.method === "PATCH") {
                const body = await readRequestBody(request);
                const payload = JSON.parse(body || "{}");
                const updatedConversation = services.chatService.updateConversation(
                    conversationMatch[1],
                    parseConversationPatch(payload)
                );
                if (!updatedConversation) {
                    sendJson(response, 404, { message: "Không tìm thấy cuộc trò chuyện." });
                    return;
                }
                sendJson(response, 200, updatedConversation);
                return;
            }

            if (conversationMatch && request.method === "DELETE") {
                const deleted = services.chatService.deleteConversation(conversationMatch[1]);
                if (!deleted) {
                    sendJson(response, 404, { message: "Không tìm thấy cuộc trò chuyện." });
                    return;
                }
                sendJson(response, 200, { ok: true });
                return;
            }

            if (pathname === "/api/chat" && request.method === "POST") {
                const body = await readRequestBody(request);
                const payload = JSON.parse(body || "{}");
                const message = typeof payload.message === "string" ? payload.message.trim() : "";
                const conversationId = typeof payload.conversationId === "string" ? payload.conversationId : undefined;
                const mode = typeof payload.mode === "string" ? payload.mode : "traditional";

                if (!message) {
                    sendJson(response, 400, { message: "Trường `message` là bắt buộc." });
                    return;
                }

                const result = await services.chatService.handleChat({ conversationId, message, mode });
                sendJson(response, 200, result);
                return;
            }

            if (pathname === "/api/model-status" && request.method === "GET") {
                sendJson(response, 200, services.chatService.getStatus());
                return;
            }

            if (pathname === "/api/health" && request.method === "GET") {
                sendJson(response, 200, {
                    ok: true,
                    dbPath: services.repository.dbPath,
                    status: services.chatService.getStatus(),
                });
                return;
            }

            sendJson(response, 404, { message: "Không tìm thấy endpoint." });
        } catch (error) {
            const statusCode = error && error.statusCode ? error.statusCode : 500;
            sendJson(response, statusCode, {
                message: statusCode === 500 ? "Lỗi server nội bộ." : String(error.message || error),
                detail: error instanceof Error ? error.message : String(error),
            });
        }
    });

    server.services = services;
    return server;
}

if (require.main === module) {
    const server = createServer();
    server.listen(config.PORT, () => {
        console.log(`Discrete Math chat server running at http://localhost:${config.PORT}`);
        console.log(`SQLite DB: ${server.services.repository.dbPath}`);
    });
}

module.exports = {
    createServer,
    createServices,
};
