const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3001;
const HISTORY_FILE = path.join(__dirname, "..", "data", "history-temp.json");

function ensureHistoryFile() {
    const dirPath = path.dirname(HISTORY_FILE);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }

    if (!fs.existsSync(HISTORY_FILE)) {
        fs.writeFileSync(HISTORY_FILE, "[]", "utf8");
    }
}

function readHistory() {
    ensureHistoryFile();
    try {
        const raw = fs.readFileSync(HISTORY_FILE, "utf8");
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
        return [];
    }
}

function writeHistory(historyItems) {
    ensureHistoryFile();
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(historyItems, null, 2), "utf8");
}

function sendJson(response, statusCode, payload) {
    response.writeHead(statusCode, {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    });
    response.end(JSON.stringify(payload));
}

function handleRequest(request, response) {
    if (request.method === "OPTIONS") {
        response.writeHead(204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        });
        response.end();
        return;
    }

    if (request.url === "/api/history" && request.method === "GET") {
        const historyItems = readHistory();
        sendJson(response, 200, historyItems);
        return;
    }

    if (request.url === "/api/history" && request.method === "PUT") {
        let body = "";

        request.on("data", chunk => {
            body += chunk;
        });

        request.on("end", () => {
            try {
                const parsed = JSON.parse(body || "[]");
                if (!Array.isArray(parsed)) {
                    sendJson(response, 400, { message: "Dữ liệu lịch sử phải là mảng" });
                    return;
                }

                writeHistory(parsed);
                sendJson(response, 200, { ok: true });
            } catch (error) {
                sendJson(response, 400, { message: "JSON không hợp lệ" });
            }
        });
        return;
    }

    if (request.url === "/api/health" && request.method === "GET") {
        sendJson(response, 200, { ok: true });
        return;
    }

    sendJson(response, 404, { message: "Không tìm thấy endpoint" });
}

ensureHistoryFile();

http.createServer(handleRequest).listen(PORT, () => {
    console.log(`History server đang chạy tại http://localhost:${PORT}`);
    console.log(`Lưu dữ liệu tại: ${HISTORY_FILE}`);
});
