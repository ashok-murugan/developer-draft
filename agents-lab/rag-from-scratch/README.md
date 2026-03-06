# RAG From Scratch (No Framework)

A minimal, educational implementation of a Retrieval-Augmented Generation (RAG) system built from the ground up using core libraries. This project avoids high-level frameworks like LangChain or LlamaIndex to help you understand the underlying mechanics of RAG.

## 🚀 Overview

This system follows the classic RAG pipeline:
1.  **Ingestion**: Loading raw text documents.
2.  **Chunking**: Splitting text into manageable pieces with overlap.
3.  **Embedding**: Converting text chunks into numerical vectors using a local model (`sentence-transformers`).
4.  **Retrieval**: Finding relevant chunks for a user query using **manual Cosine Similarity** (no vector database required!).
5.  **Generation**: Augmenting a Prompt with the retrieved context and sending it to an LLM (OpenAI) for an answer.

## 🛠️ Architecture

The core logic resides in `rag_engine.py`. Here's how it works without a framework:

### 1. Manual Chunking
We split documents into fixed sizes with a sliding window (overlap) to ensure context isn't lost at the boundaries of chunks.

### 2. Local Embeddings
We use the `all-MiniLM-L6-v2` model from `sentence-transformers`. This runs locally on your machine and converts sentences into 384-dimensional vectors.

### 3. Vector Search (The "From Scratch" Way)
Instead of a complex vector database like Pinecone or Chroma, we use **Numpy** to calculate the similarity between the query vector and every chunk vector:
```python
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

### 4. LLM Prompt Construction
We take the top-K chunks and inject them into a template:
```text
Context:
[Retrieved Chunk 1]
[Retrieved Chunk 2]

Question: [User Query]
Answer:
```

## 🏃 How to Run

### Prerequisites
- Python 3.8+
- An OpenAI API Key (for the generation phase)

### Setup
1. **Clone the repository** (or navigate to the directory).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_actual_key_here
   ```
4. **Prepare Data**:
   Place your `.txt` files in the `data/` directory.

### Run the System
```bash
python main.py
```

## 💡 Examples & Expected Output

### Example 1: Asking about AI
**Query**: "What defines AI according to modern researchers?"

**Retrieved Context**:
- Source: `ai_info.txt` - "...major AI researchers who now describe AI in terms of rationality and acting rationally..."

**Expected LLM Output**:
> Based on the provided context, modern researchers define Artificial Intelligence (AI) in terms of rationality and acting rationally, rather than simply mimicking human cognitive skills like learning or problem-solving.

### Example 2: Asking about Python
**Query**: "Where does the name Python come from?"

**Retrieved Context**:
- Source: `python_info.txt` - "The name 'Python' comes from the BBC comedy series 'Monty Python's Flying Circus'..."

**Expected LLM Output**:
> The name "Python" comes from the BBC comedy series "Monty Python's Flying Circus" and has nothing to do with the snake.

## 📂 Project Structure
- `rag_engine.py`: The heart of the system (Chunking, Embedding, Retrieval, Generation).
- `main.py`: Interactive CLI to chat with your data.
- `data/`: Folder containing your knowledge base (text files).
- `requirements.txt`: Necessary Python libraries.
