import os
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2'):
        """
        Initialize the RAG Engine with an embedding model.
        """
        print(f"Loading embedding model: {embedding_model_name}...")
        self.model = SentenceTransformer(embedding_model_name)
        self.documents = []
        self.chunks = []
        self.embeddings = None
        self.openai_client = None
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)

    def load_documents(self, data_path):
        """
        Load text documents from a directory.
        """
        print(f"Loading documents from {data_path}...")
        for filename in os.listdir(data_path):
            if filename.endswith(".txt"):
                with open(os.path.join(data_path, filename), 'r', encoding='utf-8') as f:
                    self.documents.append({"name": filename, "content": f.read()})
        print(f"Loaded {len(self.documents)} documents.")

    def chunk_documents(self, chunk_size=500, overlap=50):
        """
        Split documents into overlapping chunks.
        """
        print("Chunking documents...")
        self.chunks = []
        for doc in self.documents:
            content = doc['content']
            start = 0
            while start < len(content):
                end = start + chunk_size
                chunk_text = content[start:end]
                self.chunks.append({
                    "text": chunk_text,
                    "source": doc['name'],
                    "start_char": start
                })
                start += (chunk_size - overlap)
        print(f"Created {len(self.chunks)} chunks.")

    def create_embeddings(self):
        """
        Generate embeddings for all chunks.
        """
        if not self.chunks:
            print("No chunks to embed.")
            return

        print(f"Generating embeddings for {len(self.chunks)} chunks...")
        chunk_texts = [c['text'] for c in self.chunks]
        self.embeddings = self.model.encode(chunk_texts, show_progress_bar=True)
        print("Embeddings generated.")

    def cosine_similarity(self, v1, v2):
        """
        Calculate cosine similarity between two vectors.
        (v1 . v2) / (||v1|| * ||v2||)
        """
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return dot_product / (norm_v1 * norm_v2)

    def retrieve(self, query, top_k=3):
        """
        Retrieve the most relevant chunks for a given query.
        """
        if self.embeddings is None:
            print("Embeddings not created yet.")
            return []

        print(f"Retrieving top {top_k} chunks for query: '{query}'")
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities manually (No framework!)
        similarities = []
        for i, emb in enumerate(self.embeddings):
            sim = self.cosine_similarity(query_embedding, emb)
            similarities.append((sim, i))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for sim, idx in similarities[:top_k]:
            results.append({
                "chunk": self.chunks[idx],
                "score": float(sim)
            })
        return results

    def generate_response(self, query, retrieved_chunks):
        """
        Generate an answer using the retrieved context and an LLM.
        """
        if not self.openai_client:
            return "Error: OpenAI API key not found in .env file. Please provide an API key to generate responses."

        context = "\n\n".join([f"Source: {c['chunk']['source']}\nContent: {c['chunk']['text']}" for c in retrieved_chunks])
        
        prompt = f"""You are a helpful assistant. Use the provided context to answer the user question.
If the answer is not in the context, say you don't know based on the context.

Context:
{context}

Question: {query}

Answer:"""

        print("Generating response from LLM...")
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content

if __name__ == "__main__":
    # Quick test logic
    engine = RAGEngine()
    # Mock documents for testing
    engine.documents = [{"name": "test.txt", "content": "The capital of France is Paris. It is known for the Eiffel Tower."}]
    engine.chunk_documents(chunk_size=100)
    engine.create_embeddings()
    results = engine.retrieve("What is the capital of France?")
    print(results)
