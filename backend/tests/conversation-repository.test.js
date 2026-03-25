const fs = require("fs");
const os = require("os");
const path = require("path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { ConversationRepository } = require("../conversation-repository");

test("ConversationRepository persists, updates, and deletes conversations", t => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "dm-chat-repo-"));
    const dbPath = path.join(tempDir, "chatbot.sqlite");
    const repo = new ConversationRepository({ dbPath });

    t.after(() => {
        repo.close();
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    const conversation = repo.createConversation({ title: "Demo" });
    assert.ok(conversation.id);

    repo.addMessage({
        conversationId: conversation.id,
        role: "user",
        text: "Tập con là gì?",
    });
    repo.addMessage({
        conversationId: conversation.id,
        role: "assistant",
        text: "Tập con là tập mà mọi phần tử đều thuộc tập lớn hơn.",
        mode: "theory",
        confidence: "high",
        sources: [{ id: "tap_hop::concept_note", topic: "Tập hợp", kind: "concept_note" }],
    });

    const listed = repo.listConversations();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].messageCount, 2);

    const messages = repo.getMessages(conversation.id);
    assert.equal(messages.length, 2);
    assert.equal(messages[1].role, "assistant");
    assert.equal(messages[1].mode, "theory");
    assert.equal(messages[1].sources[0].topic, "Tập hợp");

    const updated = repo.updateConversation(conversation.id, { pinned: true, grouped: true, title: "Ôn tập tập hợp" });
    assert.equal(updated.pinned, true);
    assert.equal(updated.grouped, true);
    assert.equal(updated.title, "Ôn tập tập hợp");

    const deleted = repo.deleteConversation(conversation.id);
    assert.equal(deleted, true);
    assert.equal(repo.listConversations().length, 0);
});
