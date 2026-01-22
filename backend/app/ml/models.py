"""
SIC Ultra - Modelos de Machine Learning

Implementación de modelos de IA reales para trading:
- LSTM: Predicción de precios (series temporales)
- XGBoost: Clasificación de señales (BUY/SELL/HOLD)

Estos modelos se entrenan con datos históricos y mejoran con el tiempo.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger
import joblib
import warnings
warnings.filterwarnings('ignore')

# TensorFlow/Keras para LSTM
try:
    import tensorflow as tf
    from tensorflow import keras
    from keras.models import Sequential, load_model
    from keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from keras.callbacks import EarlyStopping, ModelCheckpoint
    from keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("⚠️ TensorFlow no disponible. LSTM deshabilitado.")

# XGBoost para clasificación
try:
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("⚠️ XGBoost no disponible. Clasificador deshabilitado.")


# === Configuración ===

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# === LSTM Price Predictor ===

class LSTMPricePredictor:
    """
    Red neuronal LSTM para predicción de precios.
    
    Arquitectura:
    - Input: Secuencias de precios + indicadores técnicos
    - 2 capas LSTM con dropout
    - Output: Precio predicho para próximo período
    """
    
    def __init__(self, sequence_length: int = 60, features: int = 7):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = os.path.join(MODELS_DIR, "lstm_price_predictor.keras")
        self.scaler_path = os.path.join(MODELS_DIR, "lstm_scaler.pkl")
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Cargar modelo existente o crear uno nuevo"""
        if not TENSORFLOW_AVAILABLE:
            return
        
        if os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("✅ Modelo LSTM cargado desde disco")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando modelo: {e}")
                self._create_model()
        else:
            self._create_model()
    
    def _create_model(self):
        """Crear arquitectura LSTM"""
        if not TENSORFLOW_AVAILABLE:
            return
        
        self.model = Sequential([
            # Primera capa LSTM
            LSTM(128, return_sequences=True, 
                 input_shape=(self.sequence_length, self.features)),
            Dropout(0.2),
            BatchNormalization(),
            
            # Segunda capa LSTM
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            BatchNormalization(),
            
            # Capas densas
            Dense(32, activation='relu'),
            Dropout(0.1),
            Dense(16, activation='relu'),
            Dense(1)  # Output: precio predicho
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("🧠 Modelo LSTM creado (nuevo)")
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preparar datos para entrenamiento/predicción.
        
        Input DataFrame debe tener: close, high, low, volume, rsi, macd, atr
        """
        # Features a usar
        feature_cols = ['close', 'high', 'low', 'volume', 'rsi', 'macd', 'atr']
        available_cols = [c for c in feature_cols if c in df.columns]
        
        if len(available_cols) < 3:
            raise ValueError("Datos insuficientes. Mínimo: close, high, low")
        
        data = df[available_cols].values
        
        # Normalizar
        data_scaled = self.scaler.fit_transform(data)
        
        # Crear secuencias
        X, y = [], []
        for i in range(self.sequence_length, len(data_scaled)):
            X.append(data_scaled[i-self.sequence_length:i])
            y.append(data_scaled[i, 0])  # Predecir close
        
        return np.array(X), np.array(y)
    
    def train(self, df: pd.DataFrame, epochs: int = 50, batch_size: int = 32):
        """
        Entrenar el modelo con datos históricos.
        """
        if not TENSORFLOW_AVAILABLE:
            logger.error("TensorFlow no disponible")
            return None
        
        X, y = self.prepare_data(df)
        
        # Split train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ModelCheckpoint(self.model_path, save_best_only=True)
        ]
        
        # Entrenar
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Guardar scaler
        joblib.dump(self.scaler, self.scaler_path)
        
        logger.info(f"✅ LSTM entrenado. Val Loss: {min(history.history['val_loss']):.6f}")
        
        return history
    
    def predict(self, recent_data: pd.DataFrame) -> Optional[Dict]:
        """
        Predecir próximo precio.
        
        Args:
            recent_data: DataFrame con últimos `sequence_length` registros
            
        Returns:
            Dict con precio predicho y dirección
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return None
        
        try:
            feature_cols = ['close', 'high', 'low', 'volume', 'rsi', 'macd', 'atr']
            available_cols = [c for c in feature_cols if c in recent_data.columns]
            
            data = recent_data[available_cols].values[-self.sequence_length:]
            data_scaled = self.scaler.transform(data)
            
            X = np.array([data_scaled])
            prediction_scaled = self.model.predict(X, verbose=0)[0][0]
            
            # Desnormalizar
            dummy = np.zeros((1, len(available_cols)))
            dummy[0, 0] = prediction_scaled
            prediction = self.scaler.inverse_transform(dummy)[0, 0]
            
            current_price = recent_data['close'].iloc[-1]
            change_percent = ((prediction - current_price) / current_price) * 100
            
            if change_percent > 1:
                direction = "BULLISH"
            elif change_percent < -1:
                direction = "BEARISH"
            else:
                direction = "NEUTRAL"
            
            return {
                "predicted_price": round(prediction, 2),
                "current_price": current_price,
                "change_percent": round(change_percent, 2),
                "direction": direction,
                "confidence": min(abs(change_percent) * 10, 100),
                "model": "LSTM",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error en predicción LSTM: {e}")
            return None


# === XGBoost Signal Classifier ===

class XGBoostSignalClassifier:
    """
    Clasificador XGBoost para generar señales de trading.
    
    Clasifica en 3 categorías:
    - BUY: Señal de compra
    - SELL: Señal de venta
    - HOLD: Mantener posición
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(MODELS_DIR, "xgboost_classifier.json")
        self.scaler_path = os.path.join(MODELS_DIR, "xgb_scaler.pkl")
        self.encoder_path = os.path.join(MODELS_DIR, "xgb_encoder.pkl")
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Cargar modelo existente o crear uno nuevo"""
        if not XGBOOST_AVAILABLE:
            return
        
        if os.path.exists(self.model_path):
            try:
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoder = joblib.load(self.encoder_path)
                logger.info("✅ Modelo XGBoost cargado desde disco")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando modelo: {e}")
                self._create_model()
        else:
            self._create_model()
    
    def _create_model(self):
        """Crear modelo XGBoost con hiperparámetros optimizados"""
        if not XGBOOST_AVAILABLE:
            return
        
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softmax',
            num_class=3,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        
        # Inicializar encoder con clases
        self.label_encoder.fit(['HOLD', 'BUY', 'SELL'])
        
        logger.info("🌲 Modelo XGBoost creado (nuevo)")
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Crear features para el clasificador.
        """
        features = []
        
        # Precio relativo
        if 'close' in df.columns:
            features.append(df['close'].pct_change())
        
        # RSI
        if 'rsi' in df.columns:
            features.append(df['rsi'])
        
        # MACD
        if 'macd' in df.columns:
            features.append(df['macd'])
            features.append(df['macd'].diff())
        
        # Volatilidad (ATR)
        if 'atr' in df.columns:
            features.append(df['atr'])
        
        # Bollinger width
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            features.append((df['bb_upper'] - df['bb_lower']) / df['close'])
        
        # Volume change
        if 'volume' in df.columns:
            features.append(df['volume'].pct_change())
        
        # SMA crossover signals
        if 'close' in df.columns:
            sma_10 = df['close'].rolling(10).mean()
            sma_50 = df['close'].rolling(50).mean()
            features.append(sma_10 - sma_50)
        
        feature_df = pd.concat(features, axis=1).dropna()
        return feature_df.values
    
    def create_labels(self, df: pd.DataFrame, future_periods: int = 5) -> np.ndarray:
        """
        Crear labels basados en movimiento futuro del precio.
        
        - BUY: Si el precio sube más del 1% en próximos `future_periods`
        - SELL: Si el precio baja más del 1%
        - HOLD: Si el cambio está entre -1% y 1%
        """
        future_return = df['close'].shift(-future_periods) / df['close'] - 1
        
        labels = []
        for ret in future_return:
            if pd.isna(ret):
                labels.append('HOLD')
            elif ret > 0.01:
                labels.append('BUY')
            elif ret < -0.01:
                labels.append('SELL')
            else:
                labels.append('HOLD')
        
        return np.array(labels)
    
    def train(self, df: pd.DataFrame, future_periods: int = 5):
        """
        Entrenar el clasificador con datos históricos.
        """
        if not XGBOOST_AVAILABLE:
            logger.error("XGBoost no disponible")
            return None
        
        X = self.prepare_features(df)
        y_raw = self.create_labels(df, future_periods)
        
        # Alinear longitudes
        min_len = min(len(X), len(y_raw))
        X = X[-min_len:]
        y_raw = y_raw[-min_len:]
        
        # Encodear labels
        y = self.label_encoder.fit_transform(y_raw)
        
        # Escalar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )
        
        # Entrenar
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluar
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Guardar
        self.model.save_model(self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.label_encoder, self.encoder_path)
        
        logger.info(f"✅ XGBoost entrenado. Accuracy: {accuracy:.2%}")
        
        return {
            "accuracy": accuracy,
            "report": classification_report(
                y_test, y_pred, 
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
        }
    
    def predict(self, recent_data: pd.DataFrame) -> Optional[Dict]:
        """
        Predecir señal de trading.
        """
        if not XGBOOST_AVAILABLE or self.model is None:
            return None
        
        try:
            X = self.prepare_features(recent_data)
            if len(X) == 0:
                return None
            
            X_scaled = self.scaler.transform(X[-1:])
            
            # Predicción
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            signal = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities) * 100
            
            return {
                "signal": signal,
                "confidence": round(confidence, 1),
                "probabilities": {
                    cls: round(prob * 100, 1) 
                    for cls, prob in zip(self.label_encoder.classes_, probabilities)
                },
                "model": "XGBoost",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error en predicción XGBoost: {e}")
            return None


# === Ensemble Model ===

class EnsemblePredictor:
    """
    Modelo ensemble que combina LSTM y XGBoost.
    
    - LSTM: Predicción numérica de precio
    - XGBoost: Clasificación de señal
    - Combinar ambos para decisión final más robusta
    """
    
    def __init__(self):
        self.lstm = LSTMPricePredictor()
        self.xgb = XGBoostSignalClassifier()
        self.is_trained = False
    
    def train(self, df: pd.DataFrame):
        """Entrenar ambos modelos"""
        lstm_result = None
        xgb_result = None
        
        if TENSORFLOW_AVAILABLE:
            lstm_result = self.lstm.train(df)
        
        if XGBOOST_AVAILABLE:
            xgb_result = self.xgb.train(df)
        
        self.is_trained = True
        
        return {
            "lstm": lstm_result,
            "xgboost": xgb_result
        }
    
    def predict(self, recent_data: pd.DataFrame) -> Dict:
        """
        Predicción combinada de ambos modelos.
        """
        lstm_pred = self.lstm.predict(recent_data)
        xgb_pred = self.xgb.predict(recent_data)
        
        # Combinar resultados
        signals = []
        confidences = []
        
        if lstm_pred:
            if lstm_pred["direction"] == "BULLISH":
                signals.append("BUY")
            elif lstm_pred["direction"] == "BEARISH":
                signals.append("SELL")
            else:
                signals.append("HOLD")
            confidences.append(lstm_pred["confidence"])
        
        if xgb_pred:
            signals.append(xgb_pred["signal"])
            confidences.append(xgb_pred["confidence"])
        
        # Consenso
        if not signals:
            return {"signal": "HOLD", "confidence": 0, "consensus": False}
        
        # Si ambos modelos acuerdan
        if len(signals) == 2 and signals[0] == signals[1]:
            final_signal = signals[0]
            final_confidence = sum(confidences) / len(confidences)
            consensus = True
        elif len(signals) == 2:
            # Usar el modelo con mayor confianza
            idx = confidences.index(max(confidences))
            final_signal = signals[idx]
            final_confidence = confidences[idx] * 0.7  # Reducir por desacuerdo
            consensus = False
        else:
            final_signal = signals[0]
            final_confidence = confidences[0]
            consensus = True
        
        return {
            "signal": final_signal,
            "confidence": round(final_confidence, 1),
            "consensus": consensus,
            "lstm_prediction": lstm_pred,
            "xgboost_prediction": xgb_pred,
            "models_agree": consensus,
            "timestamp": datetime.utcnow()
        }


# === Singletons ===

_lstm_predictor: Optional[LSTMPricePredictor] = None
_xgb_classifier: Optional[XGBoostSignalClassifier] = None
_ensemble: Optional[EnsemblePredictor] = None


def get_lstm_predictor() -> LSTMPricePredictor:
    global _lstm_predictor
    if _lstm_predictor is None:
        _lstm_predictor = LSTMPricePredictor()
    return _lstm_predictor


def get_xgb_classifier() -> XGBoostSignalClassifier:
    global _xgb_classifier
    if _xgb_classifier is None:
        _xgb_classifier = XGBoostSignalClassifier()
    return _xgb_classifier


def get_ensemble() -> EnsemblePredictor:
    global _ensemble
    if _ensemble is None:
        _ensemble = EnsemblePredictor()
    return _ensemble
