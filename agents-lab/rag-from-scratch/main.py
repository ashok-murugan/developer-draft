from rag_engine import RAGEngine
import os
import sys

def main():
    print("=== Build RAG System From Scratch ===")
    
    # Initialize engine
    engine = RAGEngine()
    
    # Check if data directory exists and has files
    data_dir = "data"
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print(f"Error: Data directory '{data_dir}' is empty or does not exist.")
        return

    # 1. Load Documents
    engine.load_documents(data_dir)
    
    # 2. Chunk Documents
    engine.chunk_documents(chunk_size=300, overlap=50)
    
    # 3. Create Embeddings
    engine.create_embeddings()
    
    print("\nRAG System Ready!")
    
    while True:
        query = input("\nAsk a question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        # 4. Retrieve
        retrieved_chunks = engine.retrieve(query, top_k=2)
        
        print("\n--- Retrieved Context ---")
        for i, res in enumerate(retrieved_chunks):
            print(f"[{i+1}] Source: {res['chunk']['source']} (Score: {res['score']:.4f})")
            print(f"Content: {res['chunk']['text'][:200]}...")
        
        # 5. Generate
        answer = engine.generate_response(query, retrieved_chunks)
        
        print("\n--- LLM Response ---")
        print(answer)
        print("-" * 50)

if __name__ == "__main__":
    main()
