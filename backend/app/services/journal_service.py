"""
SIC Ultra - Trading Journal Service
Servicio para gestionar el diario de trading y calcular métricas de performance.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from datetime import datetime

from app.infrastructure.database.models import JournalEntry, VirtualTrade

class JournalService:
    @staticmethod
    def get_entries(db: Session, user_id: int):
        return db.query(JournalEntry).filter(JournalEntry.user_id == user_id).order_by(JournalEntry.created_at.desc()).all()

    @staticmethod
    def create_entry(db: Session, user_id: int, data: Dict[str, Any]):
        entry = JournalEntry(
            user_id=user_id,
            symbol=data.get("symbol", "BTCUSDT"),
            side=data.get("side", "BUY"),
            entry_price=data.get("entry_price"),
            exit_price=data.get("exit_price"),
            pnl=data.get("pnl", 0.0),
            mood=data.get("mood", "CALM"),
            strategy=data.get("strategy", "MANUAL"),
            notes=data.get("notes", ""),
            lessons=data.get("lessons", ""),
            rating=data.get("rating", 3)
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_performance_metrics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calcula KPIs profesionales: Profit Factor, Expectancy, Win Rate, etc.
        """
        # Combinamos trades del diario y trades virtuales para una visión completa
        journal_trades = db.query(JournalEntry.pnl).filter(JournalEntry.user_id == user_id).all()
        virtual_trades = db.query(VirtualTrade.pnl).join(VirtualTrade.wallet).filter(VirtualTrade.wallet_id != None).all() # Simplificado
        
        all_pnls = [t[0] for t in journal_trades] + [t[0] for t in virtual_trades if t[0] is not None]
        
        if not all_pnls:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "expectancy": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "total_pnl": 0
            }
        
        wins = [p for p in all_pnls if p > 0]
        losses = [p for p in all_pnls if p < 0]
        
        total_trades = len(all_pnls)
        win_rate = (len(wins) / total_trades) * 100
        
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        # Expectancy = (Probability of Win * Avg Win) - (Probability of Loss * Avg Loss)
        p_win = len(wins) / total_trades
        p_loss = len(losses) / total_trades
        expectancy = (p_win * avg_win) - (p_loss * abs(avg_loss))
        
        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy": round(expectancy, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "total_pnl": round(sum(all_pnls), 2)
        }
