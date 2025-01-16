import os
import json
from bs4 import BeautifulSoup

# Define the directory containing the HTML files
html_directory = './res'

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
            # Extract the question number
            question_number = block.find_previous('h1').text.strip().split('#')[-1].strip()

            # Extract the question text
            question_text = block.find('p', class_='card-text').text.strip()

            # Extract the answers
            answers = []
            ul = block.find('ul')
            if ul:
                for li in ul.find_all('li', class_='multi-choice-item'):
                    # Clean up the answer text by removing extra whitespace and newlines
                    answer_text = ' '.join(li.text.strip().split())
                    answers.append(answer_text)

            # Extract the correct answer
            correct_answer = None
            correct_answer_div = block.find('div', class_='card-text question-answer bg-light white-text')
            if correct_answer_div:
                # Look for the correct answer in a <span> with class 'correct-answer'
                correct_answer_span = correct_answer_div.find('span', class_='correct-answer')
                if correct_answer_span:
                    correct_answer = correct_answer_span.text.strip()
                else:
                    # Fallback: Look for the correct answer in the text of the div
                    correct_answer_text = correct_answer_div.text.strip()
                    if 'Correct Answer:' in correct_answer_text:
                        correct_answer = correct_answer_text.split('Correct Answer:')[-1].strip()

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