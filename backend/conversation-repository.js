const fs = require("fs");
const path = require("path");
const { randomUUID } = require("crypto");
const Database = require("better-sqlite3");

const { buildConversationTitle, safeJsonParse } = require("./utils");

class ConversationRepository {
    constructor(options = {}) {
        this.dbPath = options.dbPath;
        this.legacyHistoryPath = options.legacyHistoryPath;
        this.db = new Database(this.dbPath);
        this.db.pragma("journal_mode = WAL");
        this.db.pragma("foreign_keys = ON");
        this.ensureSchema();
        this.prepareStatements();
        this.importLegacyHistoryIfNeeded();
    }

    ensureSchema() {
        const directoryPath = path.dirname(this.dbPath);
        if (!fs.existsSync(directoryPath)) {
            fs.mkdirSync(directoryPath, { recursive: true });
        }

        this.db.exec(`
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0,
                archived INTEGER NOT NULL DEFAULT 0,
                grouped INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                text TEXT NOT NULL,
                mode TEXT,
                confidence TEXT,
                sources_json TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_created_at ON messages(conversation_id, created_at ASC);
        `);
    }

    prepareStatements() {
        this.statements = {
            countConversations: this.db.prepare("SELECT COUNT(*) AS count FROM conversations"),
            listConversations: this.db.prepare(`
                SELECT
                    c.id,
                    c.title,
                    c.pinned,
                    c.archived,
                    c.grouped,
                    c.created_at,
                    c.updated_at,
                    (
                        SELECT text FROM messages m
                        WHERE m.conversation_id = c.id
                        ORDER BY m.created_at DESC
                        LIMIT 1
                    ) AS last_message,
                    (
                        SELECT COUNT(*) FROM messages m
                        WHERE m.conversation_id = c.id
                    ) AS message_count
                FROM conversations c
                ORDER BY c.pinned DESC, c.updated_at DESC
            `),
            getConversation: this.db.prepare(`
                SELECT id, title, pinned, archived, grouped, created_at, updated_at
                FROM conversations
                WHERE id = ?
            `),
            getMessages: this.db.prepare(`
                SELECT id, conversation_id, role, text, mode, confidence, sources_json, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            `),
            countMessages: this.db.prepare("SELECT COUNT(*) AS count FROM messages WHERE conversation_id = ?"),
            insertConversation: this.db.prepare(`
                INSERT INTO conversations (id, title, pinned, archived, grouped, created_at, updated_at)
                VALUES (@id, @title, @pinned, @archived, @grouped, @created_at, @updated_at)
            `),
            insertMessage: this.db.prepare(`
                INSERT INTO messages (id, conversation_id, role, text, mode, confidence, sources_json, created_at)
                VALUES (@id, @conversation_id, @role, @text, @mode, @confidence, @sources_json, @created_at)
            `),
            touchConversation: this.db.prepare(`
                UPDATE conversations
                SET updated_at = @updated_at
                WHERE id = @id
            `),
            renameConversation: this.db.prepare(`
                UPDATE conversations
                SET title = @title, updated_at = @updated_at
                WHERE id = @id
            `),
            deleteConversation: this.db.prepare("DELETE FROM conversations WHERE id = ?"),
            deleteMessagesForConversation: this.db.prepare("DELETE FROM messages WHERE conversation_id = ?"),
        };
    }

    countConversations() {
        return this.statements.countConversations.get().count;
    }

    importLegacyHistoryIfNeeded() {
        if (!this.legacyHistoryPath || this.countConversations() > 0 || !fs.existsSync(this.legacyHistoryPath)) {
            return;
        }

        const legacyItems = safeJsonParse(fs.readFileSync(this.legacyHistoryPath, "utf8"), []);
        if (!Array.isArray(legacyItems) || legacyItems.length === 0) {
            return;
        }

        const importTransaction = this.db.transaction(items => {
            items.forEach(item => {
                const createdAt = Number(item.createdAt) || Date.now();
                const updatedAt = Number(item.updatedAt) || createdAt;
                const id = typeof item.id === "string" && item.id.trim() ? item.id : randomUUID();
                const title = item.title || buildConversationTitle(item.messages?.[0]?.text || "");

                this.statements.insertConversation.run({
                    id,
                    title,
                    pinned: item.pinned ? 1 : 0,
                    archived: item.archived ? 1 : 0,
                    grouped: item.group ? 1 : 0,
                    created_at: createdAt,
                    updated_at: updatedAt,
                });

                const messages = Array.isArray(item.messages) ? item.messages : [];
                messages.forEach((message, index) => {
                    if (!message || typeof message.text !== "string") {
                        return;
                    }

                    this.statements.insertMessage.run({
                        id: randomUUID(),
                        conversation_id: id,
                        role: message.role === "bot" ? "assistant" : "user",
                        text: message.text,
                        mode: null,
                        confidence: null,
                        sources_json: JSON.stringify([]),
                        created_at: createdAt + index,
                    });
                });
            });
        });

        importTransaction(legacyItems);
    }

    normalizeConversation(row) {
        if (!row) {
            return null;
        }

        return {
            id: row.id,
            title: row.title,
            pinned: Boolean(row.pinned),
            archived: Boolean(row.archived),
            grouped: Boolean(row.grouped),
            createdAt: row.created_at,
            updatedAt: row.updated_at,
            lastMessage: row.last_message || "",
            messageCount: row.message_count ?? undefined,
        };
    }

    normalizeMessage(row) {
        return {
            id: row.id,
            conversationId: row.conversation_id,
            role: row.role,
            text: row.text,
            mode: row.mode || null,
            confidence: row.confidence || null,
            sources: safeJsonParse(row.sources_json || "[]", []),
            createdAt: row.created_at,
        };
    }

    listConversations() {
        return this.statements.listConversations.all().map(row => this.normalizeConversation(row));
    }

    getConversation(id) {
        const row = this.statements.getConversation.get(id);
        return this.normalizeConversation(row);
    }

    getMessages(conversationId) {
        return this.statements.getMessages
            .all(conversationId)
            .map(row => this.normalizeMessage(row));
    }

    createConversation({ title, pinned = false, archived = false, grouped = false } = {}) {
        const now = Date.now();
        const id = randomUUID();
        this.statements.insertConversation.run({
            id,
            title: title || "Đoạn chat mới",
            pinned: pinned ? 1 : 0,
            archived: archived ? 1 : 0,
            grouped: grouped ? 1 : 0,
            created_at: now,
            updated_at: now,
        });
        return this.getConversation(id);
    }

    addMessage({ conversationId, role, text, mode = null, confidence = null, sources = [] }) {
        const conversation = this.getConversation(conversationId);
        if (!conversation) {
            throw new Error(`Conversation not found: ${conversationId}`);
        }

        const now = Date.now();
        this.statements.insertMessage.run({
            id: randomUUID(),
            conversation_id: conversationId,
            role,
            text,
            mode,
            confidence,
            sources_json: JSON.stringify(Array.isArray(sources) ? sources : []),
            created_at: now,
        });

        const messageCount = this.statements.countMessages.get(conversationId).count;
        if (role === "user" && messageCount === 1) {
            this.statements.renameConversation.run({
                id: conversationId,
                title: buildConversationTitle(text),
                updated_at: now,
            });
        } else {
            this.statements.touchConversation.run({ id: conversationId, updated_at: now });
        }
    }

    updateConversation(id, patch = {}) {
        const current = this.getConversation(id);
        if (!current) {
            return null;
        }

        const next = {
            title: typeof patch.title === "string" && patch.title.trim() ? patch.title.trim() : current.title,
            pinned: typeof patch.pinned === "boolean" ? patch.pinned : current.pinned,
            archived: typeof patch.archived === "boolean" ? patch.archived : current.archived,
            grouped: typeof patch.grouped === "boolean" ? patch.grouped : current.grouped,
        };

        this.db.prepare(`
            UPDATE conversations
            SET title = @title,
                pinned = @pinned,
                archived = @archived,
                grouped = @grouped,
                updated_at = @updated_at
            WHERE id = @id
        `).run({
            id,
            title: next.title,
            pinned: next.pinned ? 1 : 0,
            archived: next.archived ? 1 : 0,
            grouped: next.grouped ? 1 : 0,
            updated_at: Date.now(),
        });

        return this.getConversation(id);
    }

    deleteConversation(id) {
        const info = this.statements.deleteConversation.run(id);
        return info.changes > 0;
    }

    toLegacyRole(role) {
        return role === "assistant" ? "bot" : "user";
    }

    fromLegacyRole(role) {
        return role === "bot" ? "assistant" : "user";
    }

    listHistoryLegacyFormat() {
        const conversations = this.listConversations();
        return conversations.map(conversation => {
            const messages = this.getMessages(conversation.id).map(message => ({
                role: this.toLegacyRole(message.role),
                text: message.text,
            }));

            return {
                id: conversation.id,
                title: conversation.title,
                pinned: conversation.pinned,
                archived: conversation.archived,
                group: conversation.grouped,
                createdAt: conversation.createdAt,
                updatedAt: conversation.updatedAt,
                messages,
            };
        });
    }

    mergeLegacyHistorySnapshot(historyItems) {
        const items = Array.isArray(historyItems) ? historyItems : [];
        const transaction = this.db.transaction(snapshot => {
            snapshot.forEach(item => {
                if (!item || typeof item !== "object") {
                    return;
                }

                const now = Date.now();
                const conversationId = typeof item.id === "string" && item.id.trim() ? item.id : randomUUID();
                const createdAt = Number(item.createdAt) || now;
                const updatedAt = Number(item.updatedAt) || now;
                const title =
                    typeof item.title === "string" && item.title.trim()
                        ? item.title.trim()
                        : buildConversationTitle((item.messages && item.messages[0] && item.messages[0].text) || "");
                const pinned = Boolean(item.pinned);
                const archived = Boolean(item.archived);
                const grouped = Boolean(item.group);

                const existingConversation = this.getConversation(conversationId);
                if (!existingConversation) {
                    this.statements.insertConversation.run({
                        id: conversationId,
                        title,
                        pinned: pinned ? 1 : 0,
                        archived: archived ? 1 : 0,
                        grouped: grouped ? 1 : 0,
                        created_at: createdAt,
                        updated_at: updatedAt,
                    });
                } else {
                    const nextUpdatedAt = Math.max(existingConversation.updatedAt || 0, updatedAt);
                    this.db.prepare(`
                        UPDATE conversations
                        SET title = @title,
                            pinned = @pinned,
                            archived = @archived,
                            grouped = @grouped,
                            updated_at = @updated_at
                        WHERE id = @id
                    `).run({
                        id: conversationId,
                        title,
                        pinned: pinned ? 1 : 0,
                        archived: archived ? 1 : 0,
                        grouped: grouped ? 1 : 0,
                        updated_at: nextUpdatedAt,
                    });
                }

                const existingMessages = this.getMessages(conversationId).map(message => ({
                    role: this.toLegacyRole(message.role),
                    text: message.text,
                }));
                const incomingMessages = Array.isArray(item.messages)
                    ? item.messages
                        .filter(message => message && typeof message.text === "string")
                        .map(message => ({
                            role: message.role === "bot" ? "bot" : "user",
                            text: message.text,
                        }))
                    : [];

                // Merge incoming snapshot with existing messages so stale PUT calls from old frontend
                // do not accidentally drop assistant replies already stored on server.
                const mergedMessages = [];
                const seenKeys = new Set();
                const addMessage = message => {
                    const key = `${message.role}|${message.text}`;
                    if (seenKeys.has(key)) {
                        return;
                    }
                    seenKeys.add(key);
                    mergedMessages.push(message);
                };
                existingMessages.forEach(addMessage);
                incomingMessages.forEach(addMessage);

                this.statements.deleteMessagesForConversation.run(conversationId);
                mergedMessages.forEach((message, index) => {
                    this.statements.insertMessage.run({
                        id: randomUUID(),
                        conversation_id: conversationId,
                        role: this.fromLegacyRole(message.role),
                        text: message.text,
                        mode: null,
                        confidence: null,
                        sources_json: JSON.stringify([]),
                        created_at: createdAt + index,
                    });
                });
            });
        });

        transaction(items);
    }

    close() {
        this.db.close();
    }
}

module.exports = {
    ConversationRepository,
};
