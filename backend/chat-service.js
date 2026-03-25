class ChatService {
    constructor(options) {
        this.repository = options.repository;
        this.retrievalEngine = options.retrievalEngine;
        this.openAIService = options.openAIService;
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

    async handleChat({ conversationId, message }) {
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

        const conversationMessages = this.repository.getMessages(conversation.id);
        const retrieval = await this.retrievalEngine.search({
            message,
            conversationMessages,
            embedQuery: text => this.openAIService.embedText(text),
        });

        const generation = await this.openAIService.generateReply({
            message,
            mode: retrieval.mode,
            confidence: retrieval.confidence,
            conversationMessages,
            documents: retrieval.documents,
        });

        this.repository.addMessage({
            conversationId: conversation.id,
            role: "assistant",
            text: generation.reply,
            mode: retrieval.mode,
            confidence: retrieval.confidence,
            sources: retrieval.sources,
        });

        return {
            conversationId: conversation.id,
            reply: generation.reply,
            mode: retrieval.mode,
            confidence: retrieval.confidence,
            sources: retrieval.sources,
            provider: generation.provider,
        };
    }

    getStatus() {
        return {
            openaiConfigured: this.openAIService.isConfigured(),
            retrieval: this.retrievalEngine.getModelStatus(),
            conversationCount: this.repository.countConversations(),
        };
    }
}

module.exports = {
    ChatService,
};
