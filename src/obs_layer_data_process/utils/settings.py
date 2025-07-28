"""utils/settings.py"""

import os

from dotenv import load_dotenv


cwd = os.getcwd()
dotenv_path = os.path.join(cwd, os.getenv('ENVIRONMENT_FILE', '.env.development'))
load_dotenv(dotenv_path=dotenv_path, override=True)

BUCKET_NAME = os.environ.get('BUCKET_NAME')
OBJECT_NAME = os.environ.get('OBJECT_NAME')
QUEUE_URLS = os.environ.get('QUEUE_URLS').split(',') if os.environ.get('QUEUE_URLS') is not None else []
