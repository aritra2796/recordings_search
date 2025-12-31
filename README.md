🎙️ Recordings Search
A Python-based application to search and manage recordings stored in a database.
This project provides a simple interface to query, filter, and retrieve recordings efficiently.

📌 Features
- 🔍 Search recordings by keywords, metadata, or filters
- 🗄️ Database integration using MySQL / PyMySQL
- ⚡ Fast queries with DictCursor for JSON-like results
- 🛡️ Secure configuration with environment variables
- 🖥️ Lightweight and easy to deploy

🛠️ Tech Stack
- Python 3.9+
- PyMySQL for database connectivity

- HTML, CSS, JavaScript for frontend components

⚙️ Installation
Clone the repository:
git clone https://github.com/aritra2796/recordings_search.git
cd recordings_search


Install dependencies:
pip install -r requirements.txt



🔑 Configuration
⚠️ Do not hardcode credentials in code.
Instead, use environment variables or a .env file.
Example .env file:
DB_HOST=127.0.0.1
DB_USER=app
DB_PASSWORD=your_password_here
DB_NAME=recordings


Load environment variables in Python:
import os
import pymysql.cursors

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "cursorclass": pymysql.cursors.DictCursor
}



🚀 Usage
Run the application:
python app.py


Access the API or UI at:
http://localhost:5000


Example API request:
curl http://localhost:5000/search?query=meeting



📂 Project Structure
recordings_search/
│── app.py              # Main entry point
│── config.py           # Database configuration
│── requirements.txt    # Dependencies
│── recordings_search/  # Core package
│── README.md           # Documentation



🧪 Testing
Run unit tests:
pytest



🔒 Security Notes
- Always hide database credentials using .env or secret managers.
- Use parameterized queries to prevent SQL injection.
- Restrict database user permissions to least privilege.

🤝 Contributing
Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change
