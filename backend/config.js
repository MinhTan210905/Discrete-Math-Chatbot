const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");

module.exports = {
    PORT: Number(process.env.PORT || 3001),
    DATA_DIR,
    MODEL_PATH: path.join(DATA_DIR, "discrete_math_model.json"),
    DB_PATH: process.env.CHAT_DB_PATH || path.join(DATA_DIR, "chatbot.sqlite"),
    OPENAI_CHAT_MODEL: process.env.OPENAI_CHAT_MODEL || "gpt-5.4",
    OPENAI_EMBEDDING_MODEL: process.env.OPENAI_EMBEDDING_MODEL || "text-embedding-3-small",
    OPENAI_REASONING_EFFORT: process.env.OPENAI_REASONING_EFFORT || "medium",
    MAX_CONTEXT_MESSAGES: Number(process.env.MAX_CONTEXT_MESSAGES || 10),
    MAX_RETRIEVED_DOCS: Number(process.env.MAX_RETRIEVED_DOCS || 5),
    MAX_OUTPUT_TOKENS: Number(process.env.MAX_OUTPUT_TOKENS || 900),
    CHAT_MODE: process.env.CHAT_MODE || "traditional", // options: "traditional" or "rag"
};
