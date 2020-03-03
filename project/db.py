import os
import sqlite3
from config import DB_NAME

conn = sqlite3.connect(os.path.join('db', f'{DB_NAME}.session'))
cursor = conn.cursor()

