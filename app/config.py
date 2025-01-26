import logging
import os

# Get the absolute path to the directory containing the script
app_directory = os.path.abspath(os.path.dirname(__file__))

# Logger configuration
logging.basicConfig(
    filename=os.path.join(app_directory, 'app.log'),
    format='%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
    level="INFO"
)
logger = logging.getLogger(__name__)
