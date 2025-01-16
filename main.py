from flask import Flask, session, redirect, url_for, render_template, request
from quiz import CardList,Quiz
from flask_session import Session
import random , os , json # Add this line to import the random module

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, unique secret key


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

RES_DIR = "./res"
quiz = None

@app.route('/')
def home():
    return redirect(url_for('setup'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        num_questions = int(request.form.get('num_questions'))
        show_answer_immediately = request.form.get('show_answer_immediately', 'y').lower()
        global quiz
        session['num_questions'] = num_questions
        session['show_answer_immediately'] = show_answer_immediately
        quiz = Quiz(RES_DIR, num_questions, show_answer_immediately)
        session['quiz_cards'] = [card.to_dict() for card in quiz.quiz_cards]
        session['question_index'] = 0
        session['correct_answers'] = 0
        session['answers'] = [None] * num_questions
        return redirect(url_for('question'))
    else:
        return render_template('setup.html')

@app.route('/question', methods=['GET', 'POST'])
def question():
    quiz_cards = session.get('quiz_cards', [])
    index = session.get('question_index', 0)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'next':
            answer_index = request.form.get('answer')
            if index < len(quiz_cards):
                card = quiz_cards[index]
                answer_choices = ['A', 'B', 'C', 'D']
                user_answer = answer_choices[int(answer_index) - 1]
                if user_answer == card['correct_answer']:
                    session['correct_answers'] += 1
                session['answers'][index] = user_answer
                session['question_index'] += 1
        elif action == 'previous' and index > 0:
            session['question_index'] = index - 1
        return redirect(url_for('question'))
    else:
        if index < len(quiz_cards):
            card = quiz_cards[index]
            return render_template('question.html', card=card, index=index, total=len(quiz_cards))
        else:
            return redirect(url_for('result'))

@app.route('/result')
def result():

    correct = session.get('correct_answers', 0)
    total = len(session.get('quiz_cards', []))
    return render_template('result.html', correct=correct, total=total)

@app.route('/check_answers')
def check_answers():
    quiz_cards = session.get('quiz_cards', [])
    answers = session.get('answers', [])
    correct_answers = [card['correct_answer'] for card in quiz_cards]
    zipped_data = list(zip(quiz_cards, answers, correct_answers))
    return render_template('check_answers.html', zipped_data=zipped_data)

@app.route('/restart')
def restart():
    global quiz
    num_questions = session.get('num_questions', 10)  # Default to 10 if not set
    show_answer_immediately = session.get('show_answer_immediately', 'y')
    quiz = Quiz(RES_DIR, num_questions, show_answer_immediately)
    session['quiz_cards'] = [card.to_dict() for card in quiz.quiz_cards]
    session['question_index'] = 0
    session['correct_answers'] = 0
    session['answers'] = [None] * num_questions
    return redirect(url_for('question'))

@app.route('/restart_exam')
def restart_exam():
    session['question_index'] = 0
    session['correct_answers'] = 0
    session['answers'] = [None] * len(session.get('quiz_cards', []))
    return redirect(url_for('question'))
# Path to the JSON file
JSON_FILE_PATH = r'C:\Users\ahabdelkhalek\Downloads\tetris\ExamTopicsQuizMaker-static\questions.json'

@app.route('/study-quiz')
def study_quiz():
    # Load the JSON file
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            questions = json.load(file)
        return render_template('study_quiz.html', questions=questions)
    else:
        return "No questions found. Please generate the JSON file first."
    
if __name__ == "__main__":
    app.run(host='192.168.1.64' ,debug=True)