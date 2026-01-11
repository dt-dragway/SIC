from flask import Flask, render_template, jsonify
import logging
from trading_bot import TradingBot
from db_manager import DBManager
import pandas as pd
from datetime import datetime, timedelta

# Configuración de Logging
logging.basicConfig(
    filename='logs/sic.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
bot = TradingBot()
db = DBManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trading')
def trading():
    # Simulamos datos para el gráfico (ya que no tenemos historial real a mano)
    # Esto llena el objeto {{ datos }} y {{ prediccion }} del template trading.html
    fechas = [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(10)][::-1]
    precios = [45000 + (i * 100) + ((-1)**i * 50) for i in range(10)]
    
    datos_simulados = {
        'timestamp': {i: f for i, f in enumerate(fechas)},
        'close': {i: p for i, p in enumerate(precios)}
    }
    
    # Obtener predicción real del bot recuperado
    analisis = bot.analyze_market("BTCUSDT")
    prediccion_val = analisis['prediction'] if analisis else 0
    
    return render_template('trading.html', 
                         datos=datos_simulados, 
                         prediccion=[[prediccion_val]]) # Formato lista de lista esperado por template

@app.route('/transacciones', methods=['GET', 'POST'])
def transacciones():
    from flask import request, redirect, url_for
    
    if request.method == 'POST':
        try:
            tipo = request.form.get('tipo')
            cantidad = float(request.form.get('cantidad'))
            precio = float(request.form.get('precio'))
            
            if db.add_transaction(tipo, cantidad, precio):
                logging.info(f"Transacción agregada: {tipo} {cantidad} @ {precio}")
            else:
                logging.error("Fallo al agregar transacción")
                
            return redirect(url_for('transacciones'))
        except Exception as e:
            logging.error(f"Error en form transacciones: {e}")
    
    txs = db.get_transactions()
    return render_template('transacciones.html', transacciones=txs)

@app.route('/arbitraje')
def arbitraje():
    return render_template('arbitraje.html')

# Endpoint API para estado del bot
@app.route('/api/status')
def status():
    return jsonify({"status": "online", "model_loaded": bot.model is not None})

if __name__ == '__main__':
    logging.info("Sistema inicializado correctamente")
    # Debug=True para desarrollo, False para producción
    app.run(host='0.0.0.0', port=5000, debug=True)
