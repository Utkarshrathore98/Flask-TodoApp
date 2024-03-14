from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os
import shutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create log directory if it doesn't exist
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
log_file = os.path.join(log_dir, 'todo.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    try:
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
    except Exception as e:
        logging.error(f"Error occurred while adding new todo: {str(e)}")
    try:
        allTodo = Todo.query.all()
        return render_template('index.html', allTodo=allTodo)
    except Exception as e:
        logging.error(f"Error occurred while fetching todos: {str(e)}")
        return "An error occurred while fetching todos."

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    try:
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            todo = Todo.query.filter_by(sno=sno).first()
            todo.title = title
            todo.desc = desc
            db.session.add(todo)
            db.session.commit()
            return redirect("/")
    except Exception as e:
        logging.error(f"Error occurred while updating todo: {str(e)}")
    try:
        todo = Todo.query.filter_by(sno=sno).first()
        return render_template('update.html', todo=todo)
    except Exception as e:
        logging.error(f"Error occurred while fetching todo for update: {str(e)}")
        return "An error occurred while fetching todo for update."

@app.route('/delete/<int:sno>')
def delete(sno):
    try:
        todo = Todo.query.filter_by(sno=sno).first()
        db.session.delete(todo)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        logging.error(f"Error occurred while deleting todo: {str(e)}")
        return "An error occurred while deleting todo."

def archive_log_file():
    try:
        # Move log file to logs folder
        if os.path.exists(log_file):
            shutil.move(log_file, os.path.join(log_dir, 'todo_archive.log'))
            logging.info("Log file archived successfully.")
    except Exception as e:
        logging.error(f"Error occurred while archiving log file: {str(e)}")

if __name__ == "__main__":
    try:
        app.run(debug=True, port=9000)
    finally:
        archive_log_file()
