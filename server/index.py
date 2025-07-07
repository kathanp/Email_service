import sys
import os

# Add the app directory to Python path
current_dir = os.path.dirname(__file__)
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

from main import app

# Export the app for Vercel
app.debug = False 