# 1. Create project
mkdir cod_inventory && cd cod_inventory
git init

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment setup
cp .env.example .env
# Edit .env with your values

# 5. Database setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py load_weapons  # Load sample weapons

# 6. Start services
redis-server  # Terminal 1
celery -A cod_inventory worker --loglevel=info  # Terminal 2
python manage.py runserver  # Terminal 3
python telegram_bot/bot.py  # Terminal 4 (optional)