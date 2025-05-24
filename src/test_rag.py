# Desc: This file contains the code to interact with the LLM models and send prompts to it.
import logging
from config.config_yaml_loader import load_config
from utils.models import initialize_gemini, generate_gemini_embeddings, build_vector_store, get_relevant_context_gemini
from utils.data import read_json




logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PATH_DB_CONTEXT_JSON = config.get("paths", {}).get("rag_db_context")
GEMINI_API_KEY = config.get("gemini_api_key")

chat, client = initialize_gemini()


# 1. Read the JSON schema
print(f"Reading schema from: {PATH_DB_CONTEXT_JSON}")
data = read_json(PATH_DB_CONTEXT_JSON)

gemini_embedding_model = "gemini-embedding-exp-03-07" #"gemini-embedding-exp-03-07"#"models/embedding-001"
# 2. Generate embeddings using Gemini
print(f"Generating embeddings with model: {gemini_embedding_model}...")
embeddings_data = generate_gemini_embeddings(data, embedding_model_name=gemini_embedding_model)

print(f"Generated {len(embeddings_data)} embeddings.")

# 3. Build the vector store (in-memory)
print("Building in-memory vector store...")
vector_store = build_vector_store(embeddings_data)


print(f"Vector store built with {len(vector_store)} valid entries.")




# 4. Perform an example query
query = "cual es la marca con el mayor precio promedio por unidad en la categoría FzozJzcn en julio del 2024 en DDozPTEy y cual es el precio promedio"

print(f"\nPerforming query: '{query}'")
results = get_relevant_context_gemini(query,
                                        vector_store,
                                        threshold=0.48) # Get the top 3 most relevant


# print(results)



# llaves_unicas = list({key for item in results for key in item['metadata'].keys()})
# print(llaves_unicas)

# 5. Display results
if results:
    print("\nTop relevant results found:\n")
    for i, r in enumerate(results):
        print(f"--- Result {i+1} ---")
        print(f"Score (Cosine Similarity): {r['score']:.4f}")
        print("Metadata:", r['metadata'])
        # print(f"Text:\n{r['text']}") # Uncomment if you want to see the full text
        print("-" * 80)
else:
    print("No relevant results found for the query.")
