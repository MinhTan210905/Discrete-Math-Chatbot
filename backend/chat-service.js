const { execFile } = require("child_process");
const path = require("path");
const util = require("util");
const config = require("./config");

const execFileAsync = util.promisify(execFile);

class ChatService {
    constructor(options) {
        this.repository = options.repository;
    }

    listConversations() {
        return this.repository.listConversations();
    }

    getConversationMessages(conversationId) {
        const conversation = this.repository.getConversation(conversationId);
        if (!conversation) {
            return null;
        }

        return {
            conversation,
            messages: this.repository.getMessages(conversationId),
        };
    }

    updateConversation(conversationId, patch) {
        return this.repository.updateConversation(conversationId, patch);
    }

    deleteConversation(conversationId) {
        return this.repository.deleteConversation(conversationId);
    }

    async handleChat({ conversationId, message, mode }) {
        let conversation = conversationId ? this.repository.getConversation(conversationId) : null;
        if (conversationId && !conversation) {
            const error = new Error("Conversation not found.");
            error.statusCode = 404;
            throw error;
        }

        if (!conversation) {
            conversation = this.repository.createConversation();
        }

        this.repository.addMessage({
            conversationId: conversation.id,
            role: "user",
            text: message,
        });

        // The python brains expect the query as an argument. 
        // We will pass the query and the conversation history.
        const conversationMessages = this.repository.getMessages(conversation.id);
        const historyJson = JSON.stringify(conversationMessages);
        
        const scriptName = mode === "rag" ? "brain_rag.py" : "brain_traditional.py";
        const scriptPath = path.join(config.DATA_DIR, scriptName);

        let resultData;
        try {
            const { stdout } = await execFileAsync("python", [scriptPath, message, historyJson], {
                cwd: config.DATA_DIR,
                maxBuffer: 1024 * 1024 * 10, // 10MB buffer just in case
                env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
            });
            resultData = JSON.parse(stdout.trim());
        } catch (error) {
            console.error(`Error executing ${scriptName}:`, error);
            resultData = {
                reply: "Xin lỗi, đã có lỗi xảy ra khi kết nối tới mô hình AI (Python Brain).",
                mode: mode,
                confidence: 0,
                sources: [],
                provider: "error"
            };
        }

        this.repository.addMessage({
            conversationId: conversation.id,
            role: "assistant",
            text: resultData.reply,
            mode: resultData.mode,
            confidence: resultData.confidence || 0,
            sources: resultData.sources || [],
        });

        return {
            conversationId: conversation.id,
            reply: resultData.reply,
            mode: resultData.mode,
            confidence: resultData.confidence || 0,
            sources: resultData.sources || [],
            provider: resultData.provider || "python-brain",
        };
    }

    getStatus() {
        return {
            pythonBrainsConfigured: true,
            conversationCount: this.repository.countConversations(),
        };
    }
}

module.exports = {
    ChatService,
};
