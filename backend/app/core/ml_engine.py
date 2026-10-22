import os
import joblib

class MLEngine:
    _model = None
    _vectorizer = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
            
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, '..', 'ml', 'model.pkl')
            vectorizer_path = os.path.join(base_dir, '..', 'ml', 'vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                cls._model = joblib.load(model_path)
                cls._vectorizer = joblib.load(vectorizer_path)
                cls._initialized = True
        except Exception as e:
            print(f"ML Engine Init Error: {e}")
            
    @classmethod
    def reload(cls):
        cls._initialized = False
        cls.initialize()

    @classmethod
    def predict(cls, text: str) -> dict:
        cls.initialize()
        
        if not cls._initialized or not cls._model or not cls._vectorizer:
            return {"ml_score": 0, "active": False}
            
        try:
            # Transform text
            features = cls._vectorizer.transform([text])
            # Get probability of class 1 (phishing)
            proba = float(cls._model.predict_proba(features)[0][1])
            score = int(round(proba * 100))
            
            return {
                "ml_score": score,
                "probability": proba,
                "active": True
            }
        except Exception as e:
            print(f"ML Engine Prediction Error: {e}")
            return {"ml_score": 0, "active": False}
