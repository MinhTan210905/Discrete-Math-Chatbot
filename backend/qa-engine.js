const { RetrievalEngine } = require("./retrieval-engine");

const retrievalEngine = new RetrievalEngine();

module.exports = {
    RetrievalEngine,
    getModelStatus() {
        return retrievalEngine.getModelStatus();
    },
};
