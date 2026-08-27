from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE produtos ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1'))
    conn.commit()

print("Coluna 'ativo' adicionada com sucesso")