import google.generativeai as palm
import textwrap
import numpy as np
from numpy.linalg import norm
import pandas as pd
import faiss
from dataclasses import dataclass

@dataclass
class MyFaiss:
    def __init__(self, data):
        self.data = data
        self.embeddings = self.generate_embeddings(data)
        self.index = self.build_faiss_index(self.embeddings)

    def generate_embeddings(self, data):
        # Placeholder for embedding generation logic
        embeddings = np.random.rand(len(data), 256)  # Replace 256 with actual embedding dimension
        return embeddings

    def build_faiss_index(self, embeddings):
        # Normalize embeddings
        embeddings = embeddings / norm(embeddings, axis=1)[:, np.newaxis]

        # Build Faiss index
        index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance metric
        index.add(embeddings)
        return index

    def search(self, query):
        # Generate embedding for the query
        query_embedding = self.generate_embeddings([query])[0]
        query_embedding = query_embedding / norm(query_embedding)

        # Search in Faiss index
        distances, indices = self.index.search(np.expand_dims(query_embedding, axis=0), k=5)
        return distances, indices
    
@dataclass
class DocumentDetector:
    def __init__(self, api_key, model_index=0):
        self.api_key = api_key
        palm.configure(api_key=api_key)
        
        # Assuming you have models defined in the class
        self.models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]
        self.model = self.models[model_index]

    def embed_text(self, text):
        return palm.generate_embeddings(model=self.model, text=text)['embedding']
        
    def find_best_passage(self, query, dataframe):
        query_embedding = palm.generate_embeddings(model=self.model, text=query)
        
        # Transpose the query_embedding to match the shape of the other matrix
        query_embedding_transposed = np.transpose(query_embedding['embedding'])

        # Make sure 'Embeddings' column is present in the DataFrame
        if 'Embeddings' in dataframe.columns:
            dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding_transposed)
            idx = np.argmax(dot_products)
            return dataframe.iloc[idx]['Text']
        else:
            raise ValueError("DataFrame does not contain 'Embeddings' column.")

    def make_prompt(self, query, relevant_passage):
        escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
        prompt = textwrap.dedent("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
        However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
        strike a friendly and conversational tone. \
        If the passage is irrelevant to the answer, you may ignore it.
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'

            ANSWER:
        """).format(query=query, relevant_passage=escaped)

        return prompt

    def get_answer(self, query, documents):
        # Assuming you have a DataFrame with pre-embedded texts
        df = pd.DataFrame(documents, columns=['Text'])
        df['Embeddings'] = df['Text'].apply(self.embed_text)

        passage = self.find_best_passage(query, df)
        prompt = self.make_prompt(query, passage)

        # Assuming you have the text generation code using the text model
        text_models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        text_model = text_models[0]

        answer = palm.generate_text(prompt=prompt,
                                    model=text_model,
                                    candidate_count=3,
                                    temperature=0.5,
                                    max_output_tokens=10000)

        return answer.result