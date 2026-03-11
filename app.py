import os
import streamlit as st
from pinecone import Pinecone
from sentence_transformers import CrossEncoder
import time

# --- Setup and Initialization ---
# We use st.cache_resource to load these models only once when the app starts.
# Otherwise, Streamlit would reload them every time you click a button!

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

@st.cache_resource
def init_pinecone():
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        st.error("PINECONE_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    return Pinecone(api_key=api_key)

@st.cache_resource
def load_reranker():
    # Loads the Cross-Encoder model locally
    return CrossEncoder("BAAI/bge-reranker-base")

import pandas as pd

# Load dataset once to use as our "Database"
@st.cache_data
def load_dataset():
    data_path = "/Users/madp/Documents/Data/develop/pinecone-hybrid-search/AMAQA-main/data/hotel_reviews/hotel_reviews.csv"
    df = pd.read_csv(data_path, nrows=500)
    # We indexed them sequentially from 'review_0' to 'review_499' based on order
    # Let's create an 'id' column mapping exactly to what Pinecone returns
    df = df.dropna(subset=['reviews.text']).reset_index(drop=True)
    df['id'] = [f"review_{i}" for i in range(len(df))]
    return df.set_index('id')

pc = init_pinecone()
reranker = load_reranker()
df_db = load_dataset()

INDEX_NAME = "multilingual-e5-large-index"
MODEL_NAME = "multilingual-e5-large"
index = pc.Index(INDEX_NAME)

# --- Streamlit UI ---
st.set_page_config(page_title="Pinecone Hybrid Search", layout="wide")

st.title("🏨 Hotel Review Hybrid Search Engine")
st.markdown("""
This app demonstrates a **Hybrid Search Pipeline** with the **Database Fetch Concept**:
1. **Vector Search (Pinecone)**: Instantly finds the closest matches using dense embeddings. Our metadata payload in Pinecone is extremely lightweight (only City and Hotel Name).
2. **Database Lookup**: Uses the Pinecone ID results to fetch the actual review text from our local CSV (simulating a SQL/NoSQL database).
3. **Reranking (Local Cross-Encoder)**: Reads the text and assigns a highly accurate semantic relevance score using `BAAI/bge-reranker-base`.
""")

# Hardcoded values for the search parameters
top_k_retrieve = 50
top_k_rerank = 5

# Main query input
query_text = st.text_input("Enter your search query (e.g., 'Dirty room with rude staff', 'Great location near the park', 'Loud dogs barking'):")

if st.button("Search", type="primary") and query_text:
    with st.spinner("Embedding query, retrieving from Pinecone, fetching from CSV, and reranking..."):
        
        start_time = time.time()
        
        # 1. Embed the query using Pinecone Inference
        try:
            embeddings = pc.inference.embed(
                model=MODEL_NAME,
                inputs=[query_text],
                parameters={"input_type": "query", "truncate": "END"}
            )
            query_vector = embeddings[0].values
        except Exception as e:
            st.error(f"Error connecting to Pinecone Inference: {e}")
            st.stop()

        # 2. Pinecone Retrieval (Pre-filtering)
        try:
            # We removed the user_id metadata, so we just run a pure global vector search
            fetch_response = index.query(
                vector=query_vector,
                top_k=top_k_retrieve,
                include_metadata=True,
                filter = {"city": "New York"}
            )
            matches = fetch_response.get("matches", [])
        except Exception as e:
            st.error(f"Error querying Pinecone index: {e}")
            st.stop()

        if not matches:
            st.warning("No documents found matching that query.")
            st.stop()

        # 3. Database Text Fetch & Prepare for Reranking
        rerank_pairs = []
        valid_matches = []
        for match in matches:
            doc_id = match['id']
            # Simulated DB lookup: Get text from the fast in-memory Pandas dataframe
            if doc_id in df_db.index:
                text_chunk = df_db.loc[doc_id, 'reviews.text']
                if pd.notna(text_chunk):
                    # Attach the text we fetched back into the match object so we have it for display later
                    match['fetched_text'] = str(text_chunk) 
                    rerank_pairs.append([query_text, str(text_chunk)])
                    valid_matches.append(match)

        # 4. Rerank using local Cross-Encoder
        if rerank_pairs:
            scores = reranker.predict(rerank_pairs)
            
            for i, match in enumerate(valid_matches):
                match["rerank_score"] = float(scores[i])
                
            # Sort by rerank score descending
            reranked_results = sorted(valid_matches, key=lambda x: x["rerank_score"], reverse=True)
            final_results = reranked_results[:top_k_rerank]
            
            end_time = time.time()
            
            st.success(f"Search completed in {end_time - start_time:.2f} seconds!")
            
            # --- Display Results ---
            st.subheader(f"Top {len(final_results)} Results")
            
            for i, res in enumerate(final_results):
                metadata = res["metadata"]
                fetched_text = res.get("fetched_text", "No text found.")
                
                with st.container():
                    st.markdown(f"### {i+1}. {metadata.get('hotel_name', 'Unknown Hotel')}")
                    st.caption(f"📍 {metadata.get('city', 'Unknown City')} | 🆔 ID: `{res['id']}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Rerank Score (Local Model)", f"{res['rerank_score']:.4f}")
                    with col2:
                        st.metric("Vector Score (Pinecone)", f"{res['score']:.4f}")
                        
                    st.info(fetched_text)
                    st.divider()
