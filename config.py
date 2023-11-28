from typing import Optional
import os

"""Global Variables"""
LANGUAGE: Optional[str] = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
POSTINGS_DIR = os.path.join(DATA_DIR, 'postings')
WEIGHTS_DIR = os.path.join(DATA_DIR, 'weights')

DB_PATH = os.path.join(DB_DIR, 'index.db')
POSTINGS_FILE_PATH = os.path.join(POSTINGS_DIR, 'postings.bin')
DOC_WEIGHTS_FILE_PATH = os.path.join(WEIGHTS_DIR, 'docWeights.bin')

# Ensure directories exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(POSTINGS_DIR, exist_ok=True)
os.makedirs(WEIGHTS_DIR, exist_ok=True)
