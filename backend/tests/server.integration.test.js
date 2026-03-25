const fs = require("fs");
const os = require("os");
const path = require("path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { createServer } = require("../server");
const { OpenAIService } = require("../openai-service");

function listen(server) {
    return new Promise(resolve => {
        server.listen(0, () => resolve(server.address()));
    });
}

test("Chat API handles greeting naturally and persists follow-up turns", async t => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "dm-chat-server-"));
    const dbPath = path.join(tempDir, "chatbot.sqlite");
    const modelPath = path.join(__dirname, "..", "..", "data", "discrete_math_model.json");
    const server = createServer({
        dbPath,
        modelPath,
        legacyHistoryPath: null,
        openAIService: new OpenAIService({ apiKey: "" }),
    });

    t.after(() => {
        server.services.repository.close();
        server.close();
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    const address = await listen(server);
    const baseUrl = `http://127.0.0.1:${address.port}`;

    const greetingResponse = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "chào bạn nha" }),
    });
    const greetingPayload = await greetingResponse.json();

    assert.equal(greetingResponse.status, 200);
    assert.equal(greetingPayload.mode, "greeting");
    assert.equal(greetingPayload.sources.length, 0);
    assert.match(greetingPayload.reply.toLowerCase(), /chào bạn|toán rời rạc/);

    const firstResponse = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            conversationId: greetingPayload.conversationId,
            message: "Tập con là gì?",
        }),
    });
    const firstPayload = await firstResponse.json();

    assert.equal(firstResponse.status, 200);
    assert.ok(firstPayload.reply.length > 0);
    assert.equal(firstPayload.mode, "theory");

    const messagesAfterFirstTurnResponse = await fetch(`${baseUrl}/api/conversations/${firstPayload.conversationId}/messages`);
    const messagesAfterFirstTurn = await messagesAfterFirstTurnResponse.json();
    assert.equal(messagesAfterFirstTurn.messages.length, 4);
    assert.deepEqual(
        messagesAfterFirstTurn.messages.map(message => message.role),
        ["user", "assistant", "user", "assistant"]
    );

    const followUpResponse = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            conversationId: firstPayload.conversationId,
            message: "Giải kỹ hơn từng bước giúp mình được không?",
        }),
    });
    const followUpPayload = await followUpResponse.json();

    assert.equal(followUpResponse.status, 200);
    assert.equal(followUpPayload.mode, "follow_up");

    const messagesAfterFollowUpResponse = await fetch(`${baseUrl}/api/conversations/${firstPayload.conversationId}/messages`);
    const messagesAfterFollowUp = await messagesAfterFollowUpResponse.json();
    assert.equal(messagesAfterFollowUp.messages.length, 6);
    assert.deepEqual(
        messagesAfterFollowUp.messages.map(message => message.role),
        ["user", "assistant", "user", "assistant", "user", "assistant"]
    );

    const conversationsResponse = await fetch(`${baseUrl}/api/conversations`);
    const conversations = await conversationsResponse.json();
    assert.equal(conversations.length, 1);
    assert.equal(conversations[0].messageCount, 6);
});
