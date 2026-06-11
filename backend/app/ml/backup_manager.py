"""
SIC Ultra - Backup Manager

Sistema automático de backups para agent_memory.json
Con rotación de 30 días y compresión opcional.
"""

import os
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class BackupManager:
    """
    Gestor de backups automáticos con rotación.
    
    Funcionalidades:
    - Crear backups con timestamp
    - Rotación automática (eliminar antiguos)
    - Compresión opcional
    - Recuperación de backups
    """
    
    def __init__(self, source_file: str, backup_dir: str = "backups", retention_days: int = 30):
        """
        Inicializar backup manager.
        
        Args:
            source_file: Archivo fuente a respaldar
            backup_dir: Directorio donde guardar backups
            retention_days: Días de retención de backups
        """
        self.source_file = Path(source_file)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        
        # Crear directorio de backups si no existe
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BackupManager inicializado: {self.source_file} -> {self.backup_dir}")
    
    def create_backup(self) -> Path:
        """
        Crear backup con timestamp.
        
        Returns:
            Path del backup creado
        """
        if not self.source_file.exists():
            logger.warning(f"Archivo fuente no existe: {self.source_file}")
            return None
        
        # Generar nombre con timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        source_name = self.source_file.stem  # Nombre sin extensión
        source_ext = self.source_file.suffix  # Extensión (.json)
        
        backup_name = f"{source_name}_{timestamp}{source_ext}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Copiar archivo
            shutil.copy2(self.source_file, backup_path)
            logger.info(f"✅ Backup creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None
    
    def rotate_backups(self, days: int = None):
        """
        Eliminar backups más antiguos del tiempo de retención.
        
        Args:
            days: Días de retención (None = usar self.retention_days)
        """
        if days is None:
            days = self.retention_days
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Buscar todos los backups
        source_name = self.source_file.stem
        pattern = str(self.backup_dir / f"{source_name}_*.json")
        
        deleted_count = 0
        for backup_file in glob.glob(pattern):
            try:
                # Obtener fecha de modificación
                file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                
                if file_time < cutoff_date:
                    os.remove(backup_file)
                    deleted_count += 1
                    logger.debug(f"Backup eliminado (antiguo): {Path(backup_file).name}")
                    
            except Exception as e:
                logger.warning(f"Error eliminando backup {backup_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  Rotación completada: {deleted_count} backups eliminados")
    
    def list_backups(self) -> list:
        """
        Listar todos los backups disponibles.
        
        Returns:
            Lista de tuplas (path, timestamp)
        """
        source_name = self.source_file.stem
        pattern = str(self.backup_dir / f"{source_name}_*.json")
        
        backups = []
        for backup_file in sorted(glob.glob(pattern), reverse=True):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                backups.append((Path(backup_file), file_time))
            except:
                pass
        
        return backups
    
    def get_latest_backup(self) -> Path:
        """
        Obtener el backup más reciente.
        
        Returns:
            Path del backup más reciente o None
        """
        backups = self.list_backups()
        if backups:
            return backups[0][0]  # El primero de la lista ordenada
        return None
    
    def restore_from_backup(self, backup_path: Path = None) -> bool:
        """
        Restaurar desde un backup.
        
        Args:
            backup_path: Path del backup (None = usar el más reciente)
            
        Returns:
            True si se restauró exitosamente
        """
        if backup_path is None:
            backup_path = self.get_latest_backup()
        
        if backup_path is None or not backup_path.exists():
            logger.error("No hay backup disponible para restaurar")
            return False
        
        try:
            # Hacer backup del archivo actual antes de restaurar
            if self.source_file.exists():
                temp_backup = self.source_file.with_suffix('.json.before_restore')
                shutil.copy2(self.source_file, temp_backup)
                logger.info(f"Backup de seguridad creado: {temp_backup}")
            
            # Restaurar
            shutil.copy2(backup_path, self.source_file)
            logger.success(f"✅ Restaurado desde: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error restaurando backup: {e}")
            return False
    
    def get_backup_stats(self) -> dict:
        """
        Obtener estadísticas de los backups.
        
        Returns:
            Diccionario con stats
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                "total_backups": 0,
                "oldest": None,
                "newest": None,
                "total_size_mb": 0
            }
        
        total_size = sum(b[0].stat().st_size for b in backups)
        
        return {
            "total_backups": len(backups),
            "oldest": backups[-1][1] if backups else None,
            "newest": backups[0][1] if backups else None,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }


# Función de conveniencia
def auto_backup_and_rotate(source_file: str, backup_dir: str = "backups", retention_days: int = 30):
    """
    Crear backup y rotar en una sola llamada.
    
    Args:
        source_file: Archivo a respaldar
        backup_dir: Directorio de backups
        retention_days: Días de retención
    """
    manager = BackupManager(source_file, backup_dir, retention_days)
    manager.create_backup()
    manager.rotate_backups()
    
    stats = manager.get_backup_stats()
    logger.info(f"📦 Backups activos: {stats['total_backups']} ({stats['total_size_mb']} MB)")
