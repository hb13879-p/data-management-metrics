import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "JMHVqpdaUR32"
    OUTPUT_FOLDER = r"app/profiler/output_files"
    OUTPUT_FOLDER_R = r"profiler/output_files"
    ALLOWED_EXTENSIONS = ["csv"]
    UPLOAD_FOLDER = r"app/uploads"
    DEMO_DATA_SOURCE = r"app/files"
