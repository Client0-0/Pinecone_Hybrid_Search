import os
import pandas as pd
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
import time

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Initialize Pinecone
API_KEY = os.environ.get("PINECONE_API_KEY")
if not API_KEY:
    raise ValueError("PINECONE_API_KEY not found in environment variables. Please check your .env file.")
INDEX_NAME = "multilingual-e5-large-index"
MODEL_NAME = "multilingual-e5-large"
DIMENSION = 1024 # multilingual-e5-large is 1024 dims

pc = Pinecone(api_key=API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in [index.name for index in pc.list_indexes()]:
    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    # Wait for index to be ready
    while not pc.describe_index(INDEX_NAME).status['ready']:
        time.sleep(1)
else:
    print(f"Index '{INDEX_NAME}' already exists.")

index = pc.Index(INDEX_NAME)

# Load data
data_path = "/Users/madp/Documents/Data/develop/pinecone-hybrid-search/AMAQA-main/data/hotel_reviews/hotel_reviews.csv"
print(f"Loading data from {data_path}...")
# Reading first 500 rows to keep it fast
df = pd.read_csv(data_path, nrows=500)

# We will use "name" (hotel name) to simulate a tenant ID (user_id) for the hybrid search
# Or we can just create a dummy user_id, or use 'city' as the metadata to filter on.
# Let's map 'city' to a numeric user_id or just use 'city' directly for filtering. 
# But our hybrid_search.py script filters by 'user_id' strictly. Let's add a fake user_id for demonstration,
# e.g., mapping each unique city to a user_id, or just assigning user_id=123 to everything.
# Let's assign user_id=123 to all of them for the sake of the demo, or mix it up.
import random
# Give them a random user_id between 123 and 125 to demonstrate filtering later.
# df['user_id'] = [random.choice([123, 124, 125]) for _ in range(len(df))]

# Clean up NaN text
df = df.dropna(subset=['reviews.text'])

# Prepare batches
batch_size = 90
total_batches = (len(df) + batch_size - 1) // batch_size

print(f"Indexing {len(df)} rows...")
for i in tqdm(range(total_batches)):
    batch = df.iloc[i * batch_size:(i + 1) * batch_size]
    
    # Prepare text for embedding
    texts = batch['reviews.text'].tolist()
    
    # Generate embeddings using Pinecone Inference API
    embeddings = pc.inference.embed(
        model=MODEL_NAME,
        inputs=texts,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    
    # Prepare vectors for upsert
    vectors = []
    for j, row in batch.reset_index().iterrows():
        vectors.append({
            "id": f"review_{row['index']}",
            "values": embeddings[j].values,
            "metadata": {
                "hotel_name": str(row['name']),
                "city": str(row['city']),
                "review_text": str(row['reviews.text'])
            }
        })
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors)

print("Indexing complete!")
