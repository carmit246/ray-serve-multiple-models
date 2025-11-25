import requests
from fastapi import FastAPI
from ray import serve
from transformers import pipeline

app = FastAPI()

@serve.deployment
@serve.ingress(app)
class FlanT5Deployment:
    def __init__(self):
        # Use the Flan-T5-small model, which is instruction-tuned
        self.model = pipeline("text2text-generation", model="google/flan-t5-small")

    @app.get("/answer")
    def get_answer(self, text: str) -> str:
        """
        Endpoint to answer questions.
        """
        # The model is fine-tuned to understand questions directly
        result = self.model(text)
        return result[0]['generated_text']

llm_app = FlanT5Deployment.bind()

# 2. Wrap the Hugging Face pipeline in a Serve deployment
@serve.deployment
@serve.ingress(app)
class SentimentAnalysisDeployment:
    def __init__(self):
        # Load a pre-trained sentiment analysis model from Hugging Face.
        # This model is small and runs efficiently on CPU.
        self.model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    
    @app.get("/sentiment")
    def predict_sentiment(self, text: str) -> str:
        """
        Endpoint to predict the sentiment of a given text.
        """
        # Run inference on the input text.
        result = self.model(text)
        # Return the predicted label (e.g., "POSITIVE", "NEGATIVE").
        return result[0]["label"]

# 3. Create a Ray Serve applications from the deployment.
sentiment_app = SentimentAnalysisDeployment.bind()
llm_app = FlanT5Deployment.bind()