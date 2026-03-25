const fs = require("fs");

const config = require("./config");
const {
    buildSemanticVector,
    cosineDense,
    dedupeBy,
    dotProductSparse,
    normalizeText,
    tokenize,
} = require("./utils");

const GREETING_HINTS = [
    "chao",
    "xin chao",
    "chao ban",
    "hi",
    "hello",
    "hey",
    "alo",
];

const SMALL_TALK_HINTS = [
    "ban la ai",
    "ban ten gi",
    "ban giup duoc gi",
    "ban lam duoc gi",
    "ban co the giup",
    "cam on",
    "thank you",
    "thanks",
    "ok",
    "oke",
    "tam biet",
    "bye",
    "ngu ngon",
];

const LEARNING_MATERIAL_HINTS = [
    "giao trinh",
    "tai lieu",
    "pdf",
    "chuong",
    "trang",
    "bai giang",
    "theo sach",
    "theo giao trinh",
    "trong giao trinh",
    "trong tai lieu",
];

const MATH_TOPIC_HINTS = [
    "tap hop",
    "tap con",
    "logic",
    "menh de",
    "suy dien",
    "quan he",
    "ham",
    "to hop",
    "chinh hop",
    "do thi",
    "cay",
    "truy hoi",
    "boole",
    "poset",
    "hasse",
    "phan hoach",
    "song anh",
    "don anh",
    "toan roi rac",
    "chu trinh",
    "bipartite",
    "bang chan tri",
    "menh de keo theo",
    "quy tac",
    "chung minh",
    "hoan vi",
    "bao ham loai tru",
    "nguyen ly dirichlet",
];

const FOLLOW_UP_HINTS = [
    "giai ky hon",
    "giai thich them",
    "tai sao",
    "vi sao",
    "cho nay",
    "do la sao",
    "buoc nay",
    "o tren",
    "y tren",
    "tiep theo",
    "cau truoc",
    "giai lai",
    "noi ro hon",
    "lam ro hon",
    "phan nay",
];

const EXERCISE_PATTERNS = [
    /\bgiai bai\b/u,
    /\btinh\b/u,
    /\bchung minh\b/u,
    /\bdem\b/u,
    /\bbao nhieu\b/u,
    /\btim\b/u,
    /\blap\b/u,
    /\brut gon\b/u,
    /\bso cach\b/u,
    /\bxac dinh\b/u,
    /\bchung to\b/u,
    /\bsuy ra\b/u,
    /\bgiai he\b/u,
];

class RetrievalEngine {
    constructor(options = {}) {
        this.modelPath = options.modelPath || config.MODEL_PATH;
        this.maxRetrievedDocs = options.maxRetrievedDocs || config.MAX_RETRIEVED_DOCS;
        this.cachedModel = null;
        this.cachedMtimeMs = 0;
    }

    loadModel() {
        if (!fs.existsSync(this.modelPath)) {
            return null;
        }

        const stats = fs.statSync(this.modelPath);
        if (!this.cachedModel || stats.mtimeMs !== this.cachedMtimeMs) {
            this.cachedModel = JSON.parse(fs.readFileSync(this.modelPath, "utf8"));
            this.cachedMtimeMs = stats.mtimeMs;
        }

        return this.cachedModel;
    }

    buildQueryVector(message, model) {
        const stopwords = new Set(model.stopwords || []);
        const tokens = tokenize(message, stopwords);
        if (tokens.length === 0) {
            return [];
        }

        const counts = new Map();
        tokens.forEach(token => {
            if (!(token in model.vocabulary)) return;
            counts.set(token, (counts.get(token) || 0) + 1);
        });

        if (counts.size === 0) {
            return [];
        }

        let norm = 0;
        const pairs = [];
        counts.forEach((count, token) => {
            const index = model.vocabulary[token];
            const tf = 1 + Math.log(count);
            const weight = tf * model.idf[index];
            pairs.push([index, weight]);
            norm += weight * weight;
        });

        norm = Math.sqrt(norm) || 1;
        return pairs
            .sort((left, right) => left[0] - right[0])
            .map(([index, weight]) => [index, weight / norm]);
    }

    containsAny(text, hints) {
        return hints.some(hint => {
            const escaped = hint.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            return new RegExp(`(^|\\s)${escaped}(?=\\s|$)`, "u").test(text);
        });
    }

    hasMathSignal(normalized) {
        return this.containsAny(normalized, MATH_TOPIC_HINTS);
    }

    isGreeting(normalized, tokenCount) {
        return tokenCount <= 6 && this.containsAny(normalized, GREETING_HINTS) && !this.hasMathSignal(normalized);
    }

    isSmallTalk(normalized, tokenCount) {
        return tokenCount <= 12 && this.containsAny(normalized, SMALL_TALK_HINTS) && !this.hasMathSignal(normalized);
    }

    mentionsLearningMaterial(normalized) {
        return this.containsAny(normalized, LEARNING_MATERIAL_HINTS);
    }

    classifyMode(message, conversationMessages = []) {
        const normalized = normalizeText(message);
        const tokenCount = normalized ? normalized.split(" ").length : 0;
        const hasRecentConversation = Array.isArray(conversationMessages) && conversationMessages.length > 1;
        const hasMathNotation = /[=<>^{}()[\]→∪∩\\]/u.test(message);
        const hasExerciseVerb = EXERCISE_PATTERNS.some(pattern => pattern.test(normalized));

        if (!normalized) {
            return "small_talk";
        }

        if (this.isGreeting(normalized, tokenCount)) {
            return "greeting";
        }

        if (this.isSmallTalk(normalized, tokenCount)) {
            return "small_talk";
        }

        if (
            hasRecentConversation &&
            tokenCount <= 16 &&
            FOLLOW_UP_HINTS.some(hint => normalized.includes(hint))
        ) {
            return "follow_up";
        }

        if (hasExerciseVerb || hasMathNotation) {
            return "exercise";
        }

        return "theory";
    }

    buildSearchText(message, conversationMessages, mode) {
        if (mode !== "follow_up") {
            return message;
        }

        const previousMessages = (conversationMessages || []).slice(0, -1);
        const context = previousMessages
            .slice(-4)
            .map(item => `${item.role === "assistant" ? "Trợ lý" : "Người dùng"}: ${item.text}`)
            .join("\n");

        return [context, `Câu hỏi tiếp theo: ${message}`].filter(Boolean).join("\n");
    }

    getConfidence(score, thresholds) {
        if (score >= thresholds.high) return "high";
        if (score >= thresholds.medium) return "medium";
        return "low";
    }

    mergeScores({ lexicalScore, semanticScore, embeddingScore, model, hasEmbeddingQuery }) {
        const weights = model.weights || { lexical: 0.6, semantic: 0.4, embedding: 0 };
        const lexicalWeight = Number(weights.lexical || 0);
        const semanticWeight = Number(weights.semantic || 0);
        const embeddingWeight = hasEmbeddingQuery ? Number(weights.embedding || 0) : 0;
        const totalWeight = lexicalWeight + semanticWeight + embeddingWeight || 1;

        return (
            lexicalScore * lexicalWeight +
            semanticScore * semanticWeight +
            embeddingScore * embeddingWeight
        ) / totalWeight;
    }

    getSourceGroup(entry) {
        if (entry.source_group === "pdf" || entry.sourceGroup === "pdf" || entry.kind === "pdf_chunk") {
            return "pdf";
        }
        return "core";
    }

    getSourceBias({ mode, sourceGroup, normalizedMessage }) {
        if (sourceGroup === "core") {
            if (mode === "theory") return 1.08;
            if (mode === "exercise") return 1.05;
            return 1;
        }

        if (this.mentionsLearningMaterial(normalizedMessage)) {
            return 1.06;
        }

        if (mode === "follow_up") {
            return 1;
        }

        return 0.82;
    }

    getRecentAcademicSources(conversationMessages = []) {
        const reversed = [...conversationMessages].reverse();
        const recentAssistant = reversed.find(
            message =>
                message.role === "assistant" &&
                !["greeting", "small_talk"].includes(message.mode) &&
                Array.isArray(message.sources) &&
                message.sources.length > 0
        );

        if (!recentAssistant) {
            return null;
        }

        const sourceIds = new Set(recentAssistant.sources.map(source => source.id));
        const sourceGroups = new Set(recentAssistant.sources.map(source => source.sourceGroup).filter(Boolean));
        return {
            ids: sourceIds,
            groups: sourceGroups,
        };
    }

    shouldUsePdf({ mode, normalizedMessage, coreCandidates, pdfCandidates, conversationMessages, thresholds }) {
        if (pdfCandidates.length === 0) {
            return false;
        }

        if (mode === "follow_up") {
            const recent = this.getRecentAcademicSources(conversationMessages);
            return Boolean(recent && recent.groups.has("pdf"));
        }

        if (this.mentionsLearningMaterial(normalizedMessage)) {
            return true;
        }

        if (coreCandidates.length === 0) {
            return true;
        }

        const topCore = coreCandidates[0]?.adjustedScore || 0;
        const topPdf = pdfCandidates[0]?.adjustedScore || 0;
        const mediumThreshold = thresholds?.medium || 0.34;

        return topCore < mediumThreshold && topPdf >= topCore * 0.95;
    }

    selectCandidates({ candidates, mode, normalizedMessage, conversationMessages, thresholds }) {
        const minQuality = 0.45;
        const filtered = candidates.filter(candidate => {
            if (candidate.adjustedScore < (thresholds?.fallback || 0.18)) {
                return false;
            }
            if (candidate.sourceGroup === "pdf" && Number(candidate.quality_score || 1) < minQuality) {
                return false;
            }
            return true;
        });

        const coreCandidates = filtered.filter(candidate => candidate.sourceGroup === "core");
        const pdfCandidates = filtered.filter(candidate => candidate.sourceGroup === "pdf");

        if (mode === "follow_up") {
            const recent = this.getRecentAcademicSources(conversationMessages);
            const prioritized = recent
                ? filtered.filter(candidate => recent.ids.has(candidate.id) || recent.groups.has(candidate.sourceGroup))
                : [];
            return dedupeBy([...prioritized, ...coreCandidates, ...pdfCandidates], candidate => candidate.id)
                .slice(0, this.maxRetrievedDocs);
        }

        let selected = coreCandidates.slice(0, this.maxRetrievedDocs);
        if (this.shouldUsePdf({ mode, normalizedMessage, coreCandidates, pdfCandidates, conversationMessages, thresholds })) {
            const pdfReserve = selected.length > 0 ? Math.min(pdfCandidates.length, mode === "exercise" ? 2 : 1) : this.maxRetrievedDocs;
            const coreLimit = Math.max(0, this.maxRetrievedDocs - pdfReserve);
            selected = coreCandidates.slice(0, coreLimit);
            const pdfLimit = Math.max(1, this.maxRetrievedDocs - selected.length);
            selected = dedupeBy([...selected, ...pdfCandidates.slice(0, pdfLimit)], candidate => candidate.id)
                .slice(0, this.maxRetrievedDocs);
        }

        if (selected.length === 0) {
            return pdfCandidates.slice(0, this.maxRetrievedDocs);
        }

        return selected;
    }

    async search({ message, conversationMessages = [], embedQuery }) {
        const mode = this.classifyMode(message, conversationMessages);
        if (mode === "greeting" || mode === "small_talk") {
            return {
                mode,
                confidence: "high",
                sources: [],
                documents: [],
                score: 1,
            };
        }

        const model = this.loadModel();
        if (!model) {
            return {
                mode,
                confidence: "low",
                sources: [],
                documents: [],
                score: 0,
            };
        }

        const searchText = this.buildSearchText(message, conversationMessages, mode);
        const normalizedMessage = normalizeText(message);
        const queryVector = this.buildQueryVector(searchText, model);
        const querySemanticVector = buildSemanticVector(searchText, model.semantic_dimensions || 256);

        let queryEmbedding = null;
        const hasDocumentEmbeddings = Boolean(model.embedding && model.embedding.enabled);
        if (hasDocumentEmbeddings && typeof embedQuery === "function") {
            try {
                queryEmbedding = await embedQuery(searchText);
            } catch (error) {
                queryEmbedding = null;
            }
        }

        const candidates = (model.entries || []).map(entry => {
            const lexicalScore = dotProductSparse(queryVector, entry.vector || []);
            const semanticScore = cosineDense(querySemanticVector, entry.semantic_vector || []);
            const embeddingScore = queryEmbedding ? cosineDense(queryEmbedding, entry.embedding || []) : 0;
            const combinedScore = this.mergeScores({
                lexicalScore,
                semanticScore,
                embeddingScore,
                model,
                hasEmbeddingQuery: Boolean(queryEmbedding),
            });
            const sourceGroup = this.getSourceGroup(entry);
            const adjustedScore = combinedScore * this.getSourceBias({ mode, sourceGroup, normalizedMessage });

            return {
                ...entry,
                sourceGroup,
                lexicalScore,
                semanticScore,
                embeddingScore,
                combinedScore,
                adjustedScore,
            };
        });

        candidates.sort((left, right) => right.adjustedScore - left.adjustedScore);
        const selected = this.selectCandidates({
            candidates,
            mode,
            normalizedMessage,
            conversationMessages,
            thresholds: model.thresholds || { high: 0.52, medium: 0.34, fallback: 0.18 },
        }).sort((left, right) => right.adjustedScore - left.adjustedScore);
        const topScore = selected[0] ? selected[0].adjustedScore : 0;
        const confidence = this.getConfidence(topScore, model.thresholds || { high: 0.52, medium: 0.34 });

        return {
            mode,
            confidence,
            score: Number(topScore.toFixed(4)),
            documents: selected,
            sources: selected.map(candidate => ({
                id: candidate.id,
                topic: candidate.topic,
                kind: candidate.kind,
                score: Number(candidate.adjustedScore.toFixed(4)),
                sourceGroup: candidate.sourceGroup,
            })),
        };
    }

    getModelStatus() {
        const model = this.loadModel();
        if (!model) {
            return {
                ok: false,
                modelLoaded: false,
                modelPath: this.modelPath,
            };
        }

        return {
            ok: true,
            modelLoaded: true,
            modelPath: this.modelPath,
            modelType: model.model_type,
            documentCount: model.document_count,
            vocabularySize: model.vocabulary_size,
            semanticDimensions: model.semantic_dimensions,
            embedding: model.embedding,
            createdAt: model.created_at,
        };
    }
}

module.exports = {
    RetrievalEngine,
};
