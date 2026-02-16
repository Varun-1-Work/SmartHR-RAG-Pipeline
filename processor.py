import chromadb
from pypdf import PdfReader
from chromadb.utils import embedding_functions
import ollama   

# Setup ChromaDB
client = chromadb.PersistentClient(path="./resume_db")
emb_fn = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="resumes", embedding_function=emb_fn)

def process_resume(file_path, filename):
    # 1. Extract Text
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    # --- DEBUG CHECK: Is the PDF empty? ---
    if len(text.strip()) < 50:
        print(f"⚠️ WARNING: Could not extract text from {filename}. It might be an image.")
        return f"Error: {filename} seems empty or scanned."

    # 2. Add to ChromaDB
    # We use the filename as the ID to prevent duplicates
    collection.add(
        documents=[text],
        ids=[filename],
        metadatas=[{"source": filename}]
    )
    return f"Processed {filename} (Length: {len(text)} chars)"

def screen_candidates(job_description):
    # 1. Ask ChromaDB for the Top 5
    results = collection.query(
        query_texts=[job_description],
        n_results=5,  
        include=['documents', 'metadatas', 'distances']
    )
    
    # Check if DB is empty
    if not results['documents'] or not results['documents'][0]:
        print("❌ Database is empty or no matches found.")
        return None

    # 2. DEBUG: Print all candidates found
    print("\n--- DEBUGGING SEARCH RESULTS ---")
    for i in range(len(results['documents'][0])):
        score = results['distances'][0][i]
        filename = results['metadatas'][0][i]['source']
        print(f"Candidate #{i+1}: {filename} (Score: {score})")

    # 3. FORCE THE BEST RESULT (Top 1)
    # ChromaDB sorts them by best match automatically, so index 0 is always the best.
    best_doc = results['documents'][0][0]
    best_score = results['distances'][0][0]

    print(f"✅ SELECTED: {results['metadatas'][0][0]['source']} with Score: {best_score}")
    
    return best_doc

def format_with_ai(messy_text):
    prompt = f"""
    You are an expert HR Assistant. 
    Below is a resume text that has formatting errors (missing spaces, no newlines).
    
    TASK:
    1. Fix the spacing errors (e.g., change "Motivatedanddetail" to "Motivated and detail").
    2. Extract the Candidate Name and Email.
    3. Summarize their skills into a clean bulleted list.
    4. Keep it concise.

    MESSY TEXT:
    {messy_text}
    """
    
    response = ollama.chat(
        model="llama3.2", 
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']