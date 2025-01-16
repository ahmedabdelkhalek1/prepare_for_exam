import os
import json
from bs4 import BeautifulSoup

# Define the directory containing the HTML files
html_directory = "./res"

# Initialize an empty list to store all questions from all files
all_questions = []

# Iterate over all HTML files in the directory
for filename in os.listdir(html_directory):
    if filename.endswith('.html'):
        # Construct the full file path
        file_path = os.path.join(html_directory, filename)
        
        # Load the HTML content
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all the question blocks
        question_blocks = soup.find_all('div', class_='question-body')

        for block in question_blocks:
            # Extract the question number and text
            question_number = block.find_previous('h1').text.split('#')[-1].strip()
            question_text = block.find('p', class_='card-text').text.strip()

            # Find the corresponding answers and correct answer
            answers = []
            correct_answer = None

            # Find the <ul> element containing the answers
            ul = block.find('ul')
            if ul:
                for li in ul.find_all('li', class_='multi-choice-item'):
                    answer_text = li.text.strip()
                    answers.append(answer_text)

            # Find the correct answer in the next sibling <div> with class 'correct-answer'
            correct_answer_div = block.find('div', class_='correct-answer-box')
            if correct_answer_div:
                correct_answer = correct_answer_div.find('span', class_='correct-answer').text.strip()

            # Append the question to the list
            all_questions.append({
                "question_number": question_number,
                "question": question_text,
                "answers": answers,
                "correct_answer": correct_answer
            })

# Convert the list to JSON
json_output = json.dumps(all_questions, indent=4)

# Save the JSON output to a file
with open('all_questions.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("JSON data has been written to all_questions.json")