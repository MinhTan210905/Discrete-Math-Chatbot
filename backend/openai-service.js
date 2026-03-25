const OpenAI = require("openai");

const config = require("./config");
const { condenseText, normalizeText, sanitizeDisplayText } = require("./utils");

class OpenAIService {
    constructor(options = {}) {
        this.chatModel = options.chatModel || config.OPENAI_CHAT_MODEL;
        this.embeddingModel = options.embeddingModel || config.OPENAI_EMBEDDING_MODEL;
        this.reasoningEffort = options.reasoningEffort || config.OPENAI_REASONING_EFFORT;
        this.maxOutputTokens = options.maxOutputTokens || config.MAX_OUTPUT_TOKENS;
        this.apiKey = options.apiKey || process.env.OPENAI_API_KEY || "";
        this.client = this.apiKey ? new OpenAI({ apiKey: this.apiKey }) : null;
    }

    isConfigured() {
        return Boolean(this.client);
    }

    async embedText(text) {
        if (!this.client || !String(text || "").trim()) {
            return null;
        }

        const response = await this.client.embeddings.create({
            model: this.embeddingModel,
            input: text,
            encoding_format: "float",
        });

        return response.data && response.data[0] ? response.data[0].embedding : null;
    }

    buildInstructions(mode) {
        const sharedRules = [
            "Bạn là trợ lý học tập Toán rời rạc, nói tiếng Việt tự nhiên, ấm áp và dễ hiểu.",
            "Hãy suy nghĩ nội bộ trước khi trả lời nhưng không tiết lộ chain-of-thought chi tiết.",
            "Nếu có tài liệu tham chiếu thì ưu tiên bám vào đó, nhưng đừng trích nguyên văn cứng nhắc.",
            "Nếu dữ kiện chưa đủ, nói rõ chỗ còn thiếu thay vì bịa thêm.",
            "Dùng công thức plain text ổn định như p -> q, A union B, not p thay vì ký hiệu dễ vỡ.",
        ];

        if (mode === "greeting") {
            sharedRules.push(
                "Người dùng chỉ đang chào hỏi. Hãy trả lời ngắn, thân thiện và mời họ đặt câu hỏi về Toán rời rạc.",
                "Không giảng bài, không nhắc nguồn, không tự mở chủ đề học thuật dài dòng."
            );
        } else if (mode === "small_talk") {
            sharedRules.push(
                "Người dùng đang hỏi xã giao hoặc hỏi bạn giúp được gì. Hãy trả lời tự nhiên như một chatbot bình thường.",
                "Có thể nhắc bạn chuyên về Toán rời rạc, nhưng không tự giảng lý thuyết nếu họ chưa hỏi."
            );
        } else if (mode === "exercise") {
            sharedRules.push(
                "Với bài tập, trình bày theo thứ tự: hiểu đề, ý tưởng làm, từng bước giải, rồi mới kết luận.",
                "Nếu đây là trắc nghiệm, vẫn giải thích vì sao đáp án đúng và vì sao hướng còn lại không phù hợp nếu cần."
            );
        } else if (mode === "follow_up") {
            sharedRules.push(
                "Với câu hỏi nối tiếp, tiếp tục đúng mạch hội thoại trước đó và chỉ đào sâu đúng chỗ người học đang hỏi."
            );
        } else {
            sharedRules.push(
                "Với câu hỏi lý thuyết, hãy bắt đầu từ ý nghĩa trực giác, rồi mới sang định nghĩa hoặc quy tắc cần nhớ.",
                "Nếu hợp lý, cho thêm một ví dụ ngắn để người học dễ hình dung."
            );
        }

        return sharedRules.join("\n");
    }

    getDocumentText(document) {
        return sanitizeDisplayText(document.normalized_content || document.content || "");
    }

    selectRelevantDocuments(documents) {
        const primary = documents[0] || null;
        if (!primary) {
            return [];
        }

        const sameTopic = documents.filter(document => document.topic === primary.topic);
        return sameTopic.length > 0 ? sameTopic : [primary];
    }

    buildInput({ message, mode, confidence, conversationMessages, documents }) {
        const history = (conversationMessages || [])
            .slice(-config.MAX_CONTEXT_MESSAGES)
            .map(item => `${item.role === "assistant" ? "Trợ lý" : "Người dùng"}: ${sanitizeDisplayText(item.text)}`)
            .join("\n");

        const knowledge = (documents || [])
            .map(document => {
                return [
                    `[${document.kind}] ${document.topic} :: ${document.title}`,
                    this.getDocumentText(document),
                    document.linked_questions && document.linked_questions.length > 0
                        ? `Câu hỏi liên quan: ${document.linked_questions.join(" | ")}`
                        : "",
                ]
                    .filter(Boolean)
                    .join("\n");
            })
            .join("\n\n");

        return [
            `CHẾ ĐỘ: ${mode}`,
            `ĐỘ TIN CẬY TRUY XUẤT: ${confidence}`,
            history ? `LỊCH SỬ GẦN ĐÂY:\n${history}` : "",
            knowledge ? `TÀI LIỆU THAM CHIẾU:\n${knowledge}` : "TÀI LIỆU THAM CHIẾU: Không cần dùng tài liệu cho lượt này.",
            `CÂU HỎI MỚI CỦA NGƯỜI DÙNG:\n${sanitizeDisplayText(message)}`,
        ]
            .filter(Boolean)
            .join("\n\n");
    }

    extractLabeledValue(text, label) {
        const pattern = new RegExp(`${label}\\s*:(.*)`, "i");
        const match = String(text || "").match(pattern);
        return match ? match[1].trim() : "";
    }

    buildGreetingReply() {
        return "Chào bạn nha. Mình ở đây để cùng bạn học Toán rời rạc, nên nếu bạn muốn ôn lý thuyết hay giải bài nào thì cứ gửi mình nhé.";
    }

    buildSmallTalkReply(message) {
        const normalized = normalizeText(message);

        if (normalized.includes("cam on") || normalized.includes("thank")) {
            return "Không có gì nè. Khi nào cần ôn lý thuyết hay giải bài Toán rời rạc thì gọi mình là được.";
        }

        if (normalized.includes("ban la ai") || normalized.includes("ban ten gi")) {
            return "Mình là trợ lý chat chuyên hỗ trợ Toán rời rạc. Mình có thể giải thích lý thuyết, gỡ từng bước bài tập và nói chuyện tự nhiên với bạn nữa.";
        }

        if (normalized.includes("ban giup duoc gi") || normalized.includes("ban lam duoc gi")) {
            return "Mình có thể giúp bạn ôn định nghĩa, giải thích khái niệm, giải bài từng bước và cùng bạn kiểm tra đáp án trong Toán rời rạc.";
        }

        if (normalized.includes("tam biet") || normalized.includes("bye") || normalized.includes("ngu ngon")) {
            return "Oke nha, khi nào cần học tiếp Toán rời rạc thì quay lại gọi mình.";
        }

        return "Mình vẫn ở đây nè. Nếu bạn muốn, mình có thể trò chuyện bình thường hoặc chuyển sang ôn Toán rời rạc ngay.";
    }

    buildTheoryReply({ documents, confidence }) {
        const relevantDocs = this.selectRelevantDocuments(documents);
        const conceptNote = relevantDocs.find(document => document.kind === "concept_note") || relevantDocs[0] || null;
        const formulaRule = relevantDocs.find(document => document.kind === "formula_rule") || null;
        const workedExample = relevantDocs.find(document => document.kind === "worked_example") || null;
        const commonMistake = relevantDocs.find(document => document.kind === "common_mistake") || null;

        if (!conceptNote) {
            return "Mình chưa thấy tài liệu khớp thật chặt cho câu này. Bạn gửi rõ khái niệm hoặc đề hơn một chút, mình sẽ giải thích bám sát hơn.";
        }

        const sections = [];
        sections.push(`Hiểu đơn giản thì ${condenseText(this.getDocumentText(conceptNote), 360)}`);

        if (formulaRule) {
            sections.push(`Điểm cần nhớ là ${condenseText(this.getDocumentText(formulaRule), 260)}`);
        }

        if (workedExample) {
            sections.push(`Ví dụ ngắn: ${condenseText(this.getDocumentText(workedExample), 260)}`);
        }

        if (commonMistake) {
            sections.push(`Lưu ý hay nhầm: ${condenseText(this.getDocumentText(commonMistake), 220)}`);
        }

        if (confidence === "low") {
            sections.push("Nếu bạn muốn, mình có thể giải thích lại theo cách chậm hơn hoặc lấy thêm ví dụ dễ hiểu hơn.");
        }

        return sections.join("\n\n");
    }

    buildExerciseReply({ message, documents, confidence }) {
        const relevantDocs = this.selectRelevantDocuments(documents);
        const conceptNote = relevantDocs.find(document => document.kind === "concept_note") || relevantDocs[0] || null;
        const formulaRule = relevantDocs.find(document => document.kind === "formula_rule") || null;
        const workedExample = relevantDocs.find(document => document.kind === "worked_example") || null;
        const questionCard = relevantDocs.find(document => document.kind === "question_card") || null;
        const answerHint = questionCard ? this.extractLabeledValue(this.getDocumentText(questionCard), "Đáp án") : "";
        const explanationHint = questionCard ? this.extractLabeledValue(this.getDocumentText(questionCard), "Giải thích") : "";

        const sections = [
            `Mình tóm tắt đề bài trước nhé: ${sanitizeDisplayText(message)}`,
            conceptNote
                ? `Ý tưởng làm là ${condenseText(this.getDocumentText(conceptNote), 320)}`
                : "Ý tưởng làm là bám vào định nghĩa hoặc quy tắc gần nhất của chủ đề này.",
        ];

        if (formulaRule) {
            sections.push(`Quy tắc cần dùng: ${condenseText(this.getDocumentText(formulaRule), 260)}`);
        }

        if (workedExample) {
            sections.push(`Một ví dụ gần giống: ${condenseText(this.getDocumentText(workedExample), 280)}`);
        }

        if (answerHint) {
            sections.push(`Từ dữ liệu hiện có, đáp án gần nhất là: ${answerHint}.`);
        }

        if (explanationHint) {
            sections.push(`Lý do là ${condenseText(explanationHint, 240)}`);
        }

        if (confidence === "low") {
            sections.push("Nếu bạn gửi nguyên đề hoặc ảnh chụp bài, mình sẽ giải sát đề hơn và trình bày từng bước rõ hơn.");
        }

        return sections.join("\n\n");
    }

    buildFollowUpReply({ conversationMessages, documents, confidence }) {
        const lastAssistant = [...(conversationMessages || [])].reverse().find(item => item.role === "assistant");
        const relevantDocs = this.selectRelevantDocuments(documents);
        const conceptNote = relevantDocs.find(document => document.kind === "concept_note") || relevantDocs[0] || null;
        const workedExample = relevantDocs.find(document => document.kind === "worked_example") || null;

        const sections = ["Mình nói kỹ hơn chỗ đó nhé."];

        if (lastAssistant) {
            sections.push(`Ý đang nối tiếp là: ${condenseText(lastAssistant.text, 260)}`);
        }

        if (conceptNote) {
            sections.push(`Giải thích thêm: ${condenseText(this.getDocumentText(conceptNote), 320)}`);
        }

        if (workedExample) {
            sections.push(`Nếu nhìn theo ví dụ thì ${condenseText(this.getDocumentText(workedExample), 260)}`);
        }

        if (confidence === "low") {
            sections.push("Nếu bạn chỉ rõ đúng dòng hoặc đúng bước đang vướng, mình sẽ bóc tách kỹ hơn đúng chỗ đó.");
        }

        return sections.join("\n\n");
    }

    buildFallbackReply(payload) {
        if (payload.mode === "greeting") {
            return this.buildGreetingReply();
        }

        if (payload.mode === "small_talk") {
            return this.buildSmallTalkReply(payload.message);
        }

        if (payload.mode === "exercise") {
            return this.buildExerciseReply(payload);
        }

        if (payload.mode === "follow_up") {
            return this.buildFollowUpReply(payload);
        }

        return this.buildTheoryReply(payload);
    }

    finalizeReply(reply) {
        return sanitizeDisplayText(reply);
    }

    async generateReply(payload) {
        if (!this.client) {
            return {
                reply: this.finalizeReply(this.buildFallbackReply(payload)),
                provider: "fallback",
                model: null,
            };
        }

        const instructions = this.buildInstructions(payload.mode);
        const input = this.buildInput(payload);

        try {
            const response = await this.client.responses.create({
                model: this.chatModel,
                instructions,
                input,
                reasoning: { effort: this.reasoningEffort },
                max_output_tokens: this.maxOutputTokens,
            });

            const reply = String(response.output_text || "").trim();
            if (!reply) {
                throw new Error("OpenAI response did not contain text output.");
            }

            return {
                reply: this.finalizeReply(reply),
                provider: "openai",
                model: this.chatModel,
            };
        } catch (error) {
            return {
                reply: this.finalizeReply(this.buildFallbackReply(payload)),
                provider: "fallback",
                model: null,
                error: error instanceof Error ? error.message : String(error),
            };
        }
    }
}

module.exports = {
    OpenAIService,
};
