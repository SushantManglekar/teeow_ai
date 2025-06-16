from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document


class VectorStore:
    """
    VectorStore handles preprocessing of dynamic API/scraped data,
    embeds it using HuggingFaceEmbeddings, and builds a FAISS vector index
    to support retrieval for Teeow.ai.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model and prepare internal vectorstore.
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        self.vectorstore = None

    def load_data(self, raw_data: List[Dict[str, Any]]):
        """
        Load and preprocess dynamic input data (from API/webscraping),
        then build a FAISS vectorstore.

        Args:
            raw_data (List[Dict]): List of input records (e.g., JSON from API).
        """
        documents = self._preprocess(raw_data)
        self.vectorstore = self._build_vectorstore(documents)

    def _preprocess(self, raw_data):
        if isinstance(raw_data[0], Document):
            return raw_data  # already preprocessed
        return [
            Document(
                page_content=item.get("content", ""),
                metadata={"title": item.get("title", "")}
            )
            for item in raw_data
        ]

    def _build_vectorstore(self, documents: List[Document]) -> FAISS:
        """
        Builds a FAISS index from the provided documents.

        Args:
            documents (List[Document]): Preprocessed documents.

        Returns:
            FAISS: Vector index ready for retrieval.
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return FAISS.from_texts(texts, self.embedding_model, metadatas=metadatas)

    def get_retriever(self, k: int = 5):
        """
        Get the retriever object for use in RAG workflows.

        Returns:
            BaseRetriever: LangChain-compatible retriever.
        """
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Call `load_data()` first.")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

if __name__ == "__main__":
    dummy_data = [
        {
            "title": "Abbey Falls",
            "description": "A scenic waterfall near Madikeri surrounded by lush coffee estates.",
            "location": "Coorg",
            "category": "nature",
            "source": "local_api"
        },
        {
            "title": "Pandi Curry at Raintree",
            "description": "Authentic Coorg pork curry served in a cozy restaurant.",
            "location": "Madikeri",
            "category": "food",
            "source": "tripadvisor"
        }
    ]

    vector_store = VectorStore()
    vector_store.load_data(dummy_data)

    retriever = vector_store.get_retriever()
    results = retriever.get_relevant_documents("Where can I try local Coorg dishes?")

    for doc in results:
        print({"content":doc.page_content, "metadata":doc.metadata})
