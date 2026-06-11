import os
import sys
import time
import json
from datetime import datetime

# Añadir el directorio backend al path para importar los modelos
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, VirtualPosition, VirtualTrade, AutomationConfig
from app.infrastructure.binance.client import get_binance_client

# Colores para la terminal
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_status_icon(enabled):
    return f"{GREEN}● ONLINE{RESET}" if enabled else f"{RED}○ OFFLINE{RESET}"

def format_pnl(val):
    color = GREEN if val >= 0 else RED
    sign = "+" if val >= 0 else ""
    return f"{color}{BOLD}{sign}{val:.2f} USDT{RESET}"

def monitor():
    db = SessionLocal()
    client = get_binance_client()
    
    try:
        while True:
            clear_screen()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Obtener Datos
            wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == 1).first()
            positions = db.query(VirtualPosition).filter(VirtualPosition.wallet_id == wallet.id).all()
            config = db.query(AutomationConfig).filter(AutomationConfig.user_id == 1).first()
            recent_trades = db.query(VirtualTrade).filter(VirtualTrade.wallet_id == wallet.id).order_by(VirtualTrade.created_at.desc()).limit(3).all()
            
            # 2. Encabezado
            print(f"{CYAN}{BOLD}============================================================{RESET}")
            print(f"{CYAN}{BOLD}   SIC ULTRA - MONITOR DE COMANDO CENTRAL (TERMINAL){RESET}")
            print(f"{CYAN}{BOLD}============================================================{RESET}")
            print(f"🕒 Hora Actual: {now} | Usuario: Admin")
            print(f"🛡️  Estado IA 24/7: {get_status_icon(config.enabled if config else False)}")
            print(f"⚙️  Modo: {YELLOW}Bajo Presupuesto ($20 Test){RESET}")
            print(f"============================================================")

            # 3. Balance
            if wallet:
                balances = json.loads(wallet.balances)
                usdt = balances.get("USDT", 0)
                print(f"{BOLD}💰 BALANCE DISPONIBLE:{RESET} {GREEN}{usdt:.2f} USDT{RESET}")
            
            # 4. Posiciones Abiertas (Futuros)
            print(f"\n{BOLD}📈 POSICIONES ACTIVAS (FUTUROS):{RESET}")
            if not positions:
                print(f"   {YELLOW}Sin posiciones abiertas.{RESET}")
            else:
                for pos in positions:
                    curr_price = client.get_price(pos.symbol)
                    pnl = (curr_price - pos.entry_price) * pos.size if pos.side == "LONG" else (pos.entry_price - curr_price) * pos.size
                    pnl_pct = (pnl / pos.margin) * 100
                    
                    print(f"   {BOLD}{pos.symbol}{RESET} | {BLUE}{pos.side} {pos.leverage}x{RESET}")
                    print(f"   Entrada: ${pos.entry_price:.4f} | Actual: ${curr_price:.4f}")
                    print(f"   Margen: ${pos.margin:.2f} | PnL: {format_pnl(pnl)} ({pnl_pct:.2f}%)")
                    print(f"   Liq. Price: {RED}${pos.liquidation_price:.4f}{RESET}")
                    print(f"   -------------------------------------------")

            # 5. Últimos Movimientos
            print(f"\n{BOLD}📋 ÚLTIMOS MOVIMIENTOS:{RESET}")
            for t in recent_trades:
                color = GREEN if t.side == "BUY" else RED
                pnl_str = f" | PnL: {format_pnl(t.pnl)}" if t.side == "SELL" else ""
                print(f"   [{t.created_at.strftime('%H:%M:%S')}] {color}{t.side}{RESET} {t.symbol} @ ${t.price:.4f}{pnl_str}")

            print(f"\n{CYAN}------------------------------------------------------------{RESET}")
            print(f"{YELLOW}Presiona Ctrl+C para salir | Actualizando cada 5s...{RESET}")
            
            db.expire_all() # Forzar recarga de datos de la DB
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n{BLUE}👋 Monitor cerrado.{RESET}")
    finally:
        db.close()

if __name__ == "__main__":
    monitor()
