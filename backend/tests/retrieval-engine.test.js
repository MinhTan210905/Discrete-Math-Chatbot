const path = require("path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { RetrievalEngine } = require("../retrieval-engine");

const MODEL_PATH = path.join(__dirname, "..", "..", "data", "discrete_math_model.json");

test("RetrievalEngine classifies greeting without retrieving documents", async () => {
    const engine = new RetrievalEngine({ modelPath: MODEL_PATH, maxRetrievedDocs: 3 });
    const result = await engine.search({
        message: "chào bạn nha",
        conversationMessages: [],
    });

    assert.equal(result.mode, "greeting");
    assert.equal(result.documents.length, 0);
    assert.equal(result.sources.length, 0);
});

test("RetrievalEngine classifies small talk without using PDF", async () => {
    const engine = new RetrievalEngine({ modelPath: MODEL_PATH, maxRetrievedDocs: 3 });
    const result = await engine.search({
        message: "bạn giúp được gì vậy",
        conversationMessages: [],
    });

    assert.equal(result.mode, "small_talk");
    assert.equal(result.documents.length, 0);
    assert.equal(result.sources.length, 0);
});

test("RetrievalEngine classifies theory questions without mislabeling 'giải thích' as exercise", async () => {
    const engine = new RetrievalEngine({ modelPath: MODEL_PATH, maxRetrievedDocs: 3 });
    const result = await engine.search({
        message: "giải thích tập con là gì",
        conversationMessages: [],
    });

    assert.equal(result.mode, "theory");
    assert.ok(result.documents.length > 0);
    assert.equal(result.documents[0].topic, "Tập hợp");
    assert.ok(result.sources.every(source => source.sourceGroup === "core"));
});

test("RetrievalEngine classifies exercise prompts and finds relevant sources", async () => {
    const engine = new RetrievalEngine({ modelPath: MODEL_PATH, maxRetrievedDocs: 4 });
    const result = await engine.search({
        message: "tính số hàm từ tập 3 phần tử sang tập 2 phần tử",
        conversationMessages: [],
    });

    assert.equal(result.mode, "exercise");
    assert.ok(result.sources.some(source => source.topic === "Hàm"));
});

test("RetrievalEngine can consult PDF when the user explicitly asks about materials", async () => {
    const engine = new RetrievalEngine({ modelPath: MODEL_PATH, maxRetrievedDocs: 4 });
    const result = await engine.search({
        message: "Trong giáo trình chương 1, quy tắc suy diễn là gì?",
        conversationMessages: [],
    });

    assert.equal(result.mode, "theory");
    assert.ok(result.sources.some(source => source.sourceGroup === "pdf"));
});
