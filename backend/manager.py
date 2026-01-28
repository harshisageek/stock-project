import os
import torch
import logging
from brain.neural_networks.data_processor import DataProcessor
from brain.neural_networks.model import StockLSTM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing ModelManager Singleton...")
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        self.device = torch.device('cpu') # Inference on CPU is sufficient
        self.processor = None
        self.model = None
        self.model_path = "brain/saved_models/hybrid_lstm.pth"
        
        # Lazy load flag
        self._loaded = False

    def load_resources(self):
        """
        Loads the DataProcessor and PyTorch Model if not already loaded.
        """
        if self._loaded:
            return

        logger.info("Loading AI Resources...")
        
        try:
            # 1. Initialize Processor (Loads Scaler)
            self.processor = DataProcessor(sequence_length=60)
            
            # 2. Initialize Model
            self.model = StockLSTM(input_size=13)
            
            if os.path.exists(self.model_path):
                logger.info(f"Loading model weights from {self.model_path}")
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()
                self._loaded = True
            else:
                logger.warning(f"Model file not found at {self.model_path}. Neural predictions will be disabled.")
                self.model = None
                
        except Exception as e:
            logger.error(f"Failed to load AI resources: {e}")
            self.model = None
            self.processor = None

    def predict_sentiment(self, graph_data):
        """
        Runs inference on the provided graph data.
        Returns: (signal: str, confidence: float)
        """
        if not self._loaded:
            self.load_resources()
            
        if not self.model or not self.processor:
            return "Neutral (Model Error)", 0.0

        try:
            # Prepare Data
            input_tensor = self.processor.prepare_inference_data(graph_data)
            
            if input_tensor is None:
                logger.warning("Insufficient data for inference (Need 60+ days).")
                return "Neutral (No Data)", 0.0
                
            # Predict
            input_tensor = torch.FloatTensor(input_tensor).to(self.device)
            
            with torch.no_grad():
                prediction = self.model(input_tensor).item()
                
            signal = "Bullish" if prediction > 0.50 else "Bearish"
            return signal, prediction
            
        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return "Neutral (Error)", 0.0

# Global Instance
model_manager = ModelManager()
