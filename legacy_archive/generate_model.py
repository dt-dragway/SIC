import xgboost as xgb
import numpy as np
import os

# Datos dummy para entrenar un modelo mínimo
X = np.array([[40000, 100, 0.5], [41000, 150, 0.6], [39000, 90, 0.4]])
y = np.array([40500, 41500, 39500])

model = xgb.XGBRegressor()
model.fit(X, y)

# Guardar modelo
model_path = 'models/arbitraje_xgboost.model'
model.save_model(model_path)
print(f"Modelo válido generado en {model_path}")
