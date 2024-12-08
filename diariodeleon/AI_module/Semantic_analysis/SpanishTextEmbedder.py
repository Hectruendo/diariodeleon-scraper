from transformers import AutoModel
import torch


class SpanishTextEmbedder:
    def __init__(self, model_name="jinaai/jina-embeddings-v2-base-es", device="cuda"):
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(device)
        self.device = device

    def embed(self, sentences):
        return self.model.encode(sentences, device=self.device)
