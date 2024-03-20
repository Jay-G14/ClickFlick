#!/bin/bash


# python3 -m http.server 8000 &

export DATABASE_URL="postgresql://jayant_g_research_ii:Vx4MigMhwy5s5jVm3DJrpw@clickflick-995.jxf.cockroachlabs.cloud:26257/clickflick?sslmode=verify-full&sslrootcert=root.crt"

# Activate the virtual environment
source venv/bin/activate
export SECRET_KEY='qeervrvpnmakswplrj562mcrorl104k5n'
# Set the FLASK_APP environment variable
export FLASK_APP=isslab3.py  # Replace with the actual name of your Flask application

# Set the FLASK_ENV environment variable to development for debugging (optional)
export FLASK_ENV=development

# Run the Flask application
flask run
