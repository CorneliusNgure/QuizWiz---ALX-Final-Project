# QuizWiz

QuizWiz is a web application that allows users to test their knowledge by taking quizzes fetched dynamically from external APIs. The app includes user authentication, tracks quiz history, and provides detailed feedback on attempted questions.

---

## **Features**
- **Dynamic Question Fetching**: Questions are pulled from a third-party API (e.g., [Open Trivia Database](https://opentdb.com)) to ensure varied and engaging content.
- **User Authentication**: Users can sign up, log in, and manage their sessions.
- **Quiz Sessions**: Tracks each quiz session and computes user scores.
- **Detailed Attempt Records**: Logs user answers and indicates correctness.
- **Database Management**: Utilizes SQLAlchemy and Flask-Migrate for data handling and migrations.
- **Flash Messages**: Provides feedback to users using dynamic flash messages.

---

## **Tech Stack**
- **Backend**: Flask, SQLAlchemy
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Fetches quiz questions from the [Open Trivia Database](https://opentdb.com)
- **Migrations**: Flask-Migrate

---

## **Getting Started**

### **Quick Start**
1. Clone the repository:
   ```bash
   git clone https://github.com/CorneliusNgure/QuizWiz.git
   cd quizwiz
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the `.env` file (see below) and set up the database.

---

### **Environment Variables**
Create a `.env` file in the root directory and add the following:

```bash
# Database configuration
DB_NAME_DEV=`your_development_db_name`
DB_NAME_TEST=`your_testing_db_name`  # optional
DB_NAME_PROD=`your_production_db_name`  # optional

DB_USERNAME=`your_mysql_username`
DB_PASSWORD=`your_mysql_password`
DB_HOST=localhost
DB_PORT=3306

# Flask configuration
FLASK_ENV=development
SECRET_KEY=`your_secret_key`
```

- Replace placeholders with actual values and ensure `.env` is excluded from version control (`.gitignore`).

---

### **Installation**

1. Ensure your MySQL server is running and create a database:
   ```sql
   CREATE DATABASE quizwiz;
   ```

2. Initialize and migrate the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

---

### **Usage**
Start the app:
- **Linux/macOS**:
   ```bash
   flask run
   ```
- **Windows**:
   ```bash
   python -m flask run
   ```

Access the app at [http://127.0.0.1:5000/home](http://127.0.0.1:5000/home).

---

### **Future Enhancements**
- **Leaderboards:** Display top quiz scorers.
- **Question Cache:** Cache questions locally to reduce API call frequency.
- **Frontend Framework:** Integrate React or Vue.js for a modern user experience.

---

### **Contributing**
Contributions are welcome! Submit issues or pull requests to help improve QuizWiz.

---

### **License**
This project is licensed under the MIT License.

---

### **Contact**
For questions or suggestions, reach out via:
- **Email:** kingcornelius07@gmail.com