const crypto = require("crypto");

const DISPLAY_REPLACEMENTS = [
    [//g, " or "],
    [/∨/g, " or "],
    [//g, " and "],
    [/∧/g, " and "],
    [//g, " not "],
    [/¬/g, " not "],
    [/→/g, " -> "],
    [/⇒/g, " -> "],
    [/↔/g, " <-> "],
    [/⇔/g, " <-> "],
    [/∪/g, " union "],
    [/∩/g, " intersection "],
    [/⊆/g, " subseteq "],
    [/⊂/g, " subset "],
    [/⊇/g, " superseteq "],
    [/⊃/g, " superset "],
    [/∈/g, " in "],
    [/∉/g, " not in "],
    [/∀/g, " voi moi "],
    [/∃/g, " ton tai "],
    [/≤/g, " <= "],
    [/≥/g, " >= "],
    [/≠/g, " != "],
    [/≈/g, " xap xi "],
];

function normalizeText(text) {
    return String(text || "")
        .toLowerCase()
        .replace(/đ/g, "d")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function normalizeFormulaText(text) {
    let output = String(text || "");
    DISPLAY_REPLACEMENTS.forEach(([pattern, replacement]) => {
        output = output.replace(pattern, replacement);
    });

    return output
        .replace(/\s*([(){}\[\],.;:])\s*/g, "$1 ")
        .replace(/\s+\n/g, "\n")
        .replace(/\n{3,}/g, "\n\n")
        .replace(/[ \t]{2,}/g, " ")
        .trim();
}

function sanitizeDisplayText(text) {
    return normalizeFormulaText(String(text || ""))
        .replace(/\r/g, "")
        .replace(/[ \t]+\n/g, "\n")
        .replace(/\n{3,}/g, "\n\n")
        .replace(/[ \t]{2,}/g, " ")
        .trim();
}

function condenseText(text, maxLength = 420) {
    const sanitized = sanitizeDisplayText(text);
    if (sanitized.length <= maxLength) {
        return sanitized;
    }

    const cutoff = sanitized.slice(0, maxLength);
    const lastBoundary = Math.max(
        cutoff.lastIndexOf(". "),
        cutoff.lastIndexOf("\n"),
        cutoff.lastIndexOf("; ")
    );
    const trimmed = lastBoundary > 120 ? cutoff.slice(0, lastBoundary + 1) : cutoff;
    return `${trimmed.trim()}...`;
}

function tokenize(text, stopwords) {
    const normalized = normalizeText(text);
    if (!normalized) return [];

    return normalized
        .split(" ")
        .filter(token => token && !(stopwords && stopwords.has(token)));
}

function semanticNgrams(text, size = 3) {
    const normalized = ` ${normalizeText(text)} `;
    if (normalized.trim().length === 0) {
        return [];
    }
    if (normalized.length < size) {
        return [normalized.trim()];
    }

    const grams = [];
    for (let index = 0; index <= normalized.length - size; index += 1) {
        grams.push(normalized.slice(index, index + size));
    }
    return grams;
}

function stableHash(value) {
    const digest = crypto.createHash("sha256").update(String(value), "utf8").digest();
    return digest.readBigUInt64BE(0);
}

function buildSemanticVector(text, dimensions = 256) {
    const grams = semanticNgrams(text);
    if (grams.length === 0) {
        return [];
    }

    const vector = new Array(dimensions).fill(0);
    grams.forEach(gram => {
        const index = Number(stableHash(gram) % BigInt(dimensions));
        const sign = stableHash(`sign::${gram}`) % 2n === 0n ? 1 : -1;
        vector[index] += sign;
    });

    const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0)) || 1;
    return vector.map(value => value / norm);
}

function dotProductSparse(left, right) {
    let i = 0;
    let j = 0;
    let score = 0;

    while (i < left.length && j < right.length) {
        const [leftIndex, leftWeight] = left[i];
        const [rightIndex, rightWeight] = right[j];

        if (leftIndex === rightIndex) {
            score += leftWeight * rightWeight;
            i += 1;
            j += 1;
            continue;
        }

        if (leftIndex < rightIndex) {
            i += 1;
        } else {
            j += 1;
        }
    }

    return score;
}

function cosineDense(left, right) {
    if (!Array.isArray(left) || !Array.isArray(right) || left.length === 0 || right.length === 0) {
        return 0;
    }

    const size = Math.min(left.length, right.length);
    let dot = 0;
    let leftNorm = 0;
    let rightNorm = 0;

    for (let index = 0; index < size; index += 1) {
        const leftValue = Number(left[index]) || 0;
        const rightValue = Number(right[index]) || 0;
        dot += leftValue * rightValue;
        leftNorm += leftValue * leftValue;
        rightNorm += rightValue * rightValue;
    }

    if (leftNorm === 0 || rightNorm === 0) {
        return 0;
    }

    return dot / (Math.sqrt(leftNorm) * Math.sqrt(rightNorm));
}

function buildConversationTitle(messageText) {
    const trimmed = String(messageText || "").trim();
    if (!trimmed) {
        return "Đoạn chat mới";
    }
    return trimmed.length > 72 ? `${trimmed.slice(0, 72)}...` : trimmed;
}

function safeJsonParse(value, fallback) {
    try {
        return JSON.parse(value);
    } catch (error) {
        return fallback;
    }
}

function dedupeBy(items, getKey) {
    const seen = new Set();
    return items.filter(item => {
        const key = getKey(item);
        if (seen.has(key)) {
            return false;
        }
        seen.add(key);
        return true;
    });
}

module.exports = {
    buildConversationTitle,
    buildSemanticVector,
    condenseText,
    cosineDense,
    dedupeBy,
    dotProductSparse,
    normalizeFormulaText,
    normalizeText,
    safeJsonParse,
    sanitizeDisplayText,
    tokenize,
};
