# Backend app module

# Override sqlite3 with pysqlite3 for ChromaDB FTS5 support
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
