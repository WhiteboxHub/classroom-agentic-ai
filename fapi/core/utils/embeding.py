from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from src.utils.logger import logger

class sentence_transformer_embeding_model(Embeddings):
            def __init__(self, s_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" ):
                self.model_name = s_model
                self.model = SentenceTransformer(self.model_name)
            
            def embed_documents(self,text : list):
                embed_doc = {}
                for doc in tqdm(text):
                    embed_doc[doc] = self.model.encode(doc).tolist()
                return embed_doc
            
            def embed_query(self,query : str):
                return self.model.encode([query])[0].tolist()