from bs4 import BeautifulSoup as bs
import os
import re

class Card:
    def __init__(self, _question: str, _answers: list, _correct_answer: str, _question_number: str) -> None:
        self.question = _question
        self.answers = _answers
        self.correct_answer = _correct_answer
        self.question_number = _question_number

    def print_card(self):
        print("="*20)
        print("Question ", self.question_number, ": ")
        print(self.question)
        print("="*20)
        print("~"*20)
        print("Answers:")
        print(self.answers)
        print("~"*20)
        print(self.correct_answer)

    def to_dict(self):
        return {
            'question': self.question,
            'answers': self.answers,
            'correct_answer': self.correct_answer,
            'question_number': self.question_number
        }


class CardList:
    """ Represents a structure that holds a list of Cards """
    def __init__(self, resources_dir) -> None:
        self.__page_soup_list = self.__init_soup(self.__get_list_of_html(resources_dir))
        self.cards_list = [] 

        for page_soup in self.__page_soup_list:
            cards_on_page = self.__get_all_cards(page_soup)
            for card in cards_on_page:
                self.cards_list.append(card)
        print(f"Loaded {len(self.cards_list)} cards.")

    def __get_list_of_html(self, resources_dir) -> list:
        """ Iterates through directory where HTML files are and returns their names """
        html = []
        for file in os.listdir(resources_dir):
            _ = os.path.join(resources_dir, file)
            if os.path.isfile(_):
                html.append(_)
        return html  # order is irrelevant

    def __init_soup(self, html_list: list):
        """ Creates a list of soups so that we can easily parse each of them """
        soup_list = [] 
        for html_file in html_list:
            with open(html_file, "r", encoding="utf8") as fhandler:
                soup = bs(fhandler.read(), "html.parser")
                soup_list.append(soup)
        return soup_list

    def __get_all_cards(self, page_soup):
        """ 
            Returns all cards (one question, 4 answers, and one correct answer) that 
            are on a page.
        """
        # Check if the page is in the new format (discussion-header-container)
        discussion_container = page_soup.find("div", class_="discussion-header-container")
        if discussion_container:
            return self.__parse_discussion_format(discussion_container)
        else:
            # Fall back to the old format (card exam-question-card)
            return self.__parse_old_format(page_soup)

    def __parse_discussion_format(self, discussion_container):
        """ Parses the new discussion format """
        cards = []
        question_body = discussion_container.find("div", class_="question-body")
        if question_body:
            question = self.__get_question(question_body)
            answers = self.__get_answers(question_body)
            correct_answer = self.__get_correct_answer(question_body)
            question_number = self.__get_question_number(discussion_container)  # Pass the discussion_container
            cards.append(Card(question, answers, correct_answer, question_number))
        return cards

    def __parse_old_format(self, page_soup):
        """ Parses the old format (card exam-question-card) """
        cards = []
        card_bodies = page_soup.find_all("div", class_="card exam-question-card")
        for card_body in card_bodies:
            question = self.__get_question(card_body)
            answers = self.__get_answers(card_body)
            correct_answer = self.__get_correct_answer(card_body)
            question_number = self.__get_question_number(card_body)
            cards.append(Card(question, answers, correct_answer, question_number))
        return cards

    def __clean_string(self, string: str) -> str:
        """ 
            Removes \n and whitespace in front and back of the string
        """
        string = re.sub(r"^[\n\s]+", "", string)
        string = re.sub(r"[\n\s]+$", "", string)  # fixed: trailing spaces are now removed
        string = re.sub(r"\n", " ", string)  # get rid of newlines in string
        string = re.sub(r"\s{2,}", " ", string)  # substitute more than 2 spaces in only 1
        string = string.rstrip()  # remove trailing space if necessary
        # get rid of Most Voted from the back of the answers
        _ = string.split(" ")
        if len(_) >= 2:
            if " ".join(_[-2:]).lower() == "most voted":  # if last 2 words are 'most voted'
                string = " ".join(_[:-2])  # get rid of them

        # get rid of some weird non-ascii chars that break the app 
        string = string.encode("ascii", errors="ignore").decode()

        return string

    def __get_question_number(self, card_body) -> str:
        """ 
            Get the question number for easier debugging purposes.
        """
        # First, check if the question number is in the old format (card-header text-white bg-primary)
        old_format_header = card_body.find("div", attrs={'class': "card-header text-white bg-primary"})
        if old_format_header:
            # Extract the question number from the old format
            return self.__clean_string(old_format_header.text).split(" ")[1]

        # If the old format is not found, check the new format (discussion-header-container)
        question_header = card_body.find("div", class_="question-discussion-header")
        if question_header:
            # Extract the text from the question header
            question_text = question_header.get_text(separator=" ")
            # Use regex to find the question number
            match = re.search(r"Question\s*#:\s*(\d+)", question_text)
            if match:
                return f"#{match.group(1)}" # Return the question number with '#' before it

        # If neither format is found, return "Unknown"
        return "Unknown"

    def __get_question(self, card_body) -> str:
        """ 
            Returns the question available in the body of this card
        """
        question = card_body.find("p", class_="card-text")
        if question:
            return self.__clean_string(question.text)
        return "No question found"

    def __get_answers(self, card_body) -> list:
        """ 
            Returns the four answers available in the body of this card
        """
        answers = card_body.find_all("li", class_="multi-choice-item")
        if answers:
            return [self.__clean_string(_.text) for _ in answers]
        return []

    def __get_correct_answer(self, card_body) -> str:
        """ 
            Returns the correct answer from a card.
        """
        correct_answer = card_body.find("span", class_="correct-answer")
        if correct_answer:
            return self.__clean_string(correct_answer.text)
        return "No correct answer found"

    def get_cards(self) -> list:
        """ 
            Getter for the list of cards    
        """
        return self.cards_list