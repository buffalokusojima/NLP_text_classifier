from wakati import wakati_class
from tfidf import tfidf_class

ROOT_DIR = '.'
DATA_PATH = '/text'
DATA_FILE_NAME = '.txt'

#wakati = wakati_class.Wakati(DATA_FILE_NAME, ROOT_DIR, ROOT_DIR)

#wakati.show_path()
#wakati.wakati()


tfidf = tfidf_class.TF_IDF(ROOT_DIR+ROOT_DIR+DATA_PATH, ROOT_DIR+ROOT_DIR+DATA_PATH)
tfidf.show_path()
tfidf.tfidf_medium()
