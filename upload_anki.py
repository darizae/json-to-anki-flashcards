import json
import re
import requests
import argparse
import os
import sys


def preprocess_json_content(text):
    # Replace escaped double quotes with single quotes
    text = re.sub(r'\\"', "'", text)
    # Double escape backslashes for LaTeX, if not already escaped
    text = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', text)
    return text


def create_deck(deck_name):
    try:
        payload = json.dumps({
            "action": "createDeck",
            "version": 6,
            "params": {
                "deck": deck_name
            }
        })
        response = requests.post('http://localhost:8765', data=payload)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(
            "Anki is not reachable. Make sure Anki is running and configured to accept connections on 'http://localhost:8765'")
        sys.exit(1)


def add_note(question, answer, deck_name):
    try:
        payload = json.dumps({
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": "Basic",
                    "fields": {
                        "Front": question,
                        "Back": answer
                    },
                    "options": {
                        "allowDuplicate": False
                    },
                    "tags": []
                }
            }
        })
        response = requests.post('http://localhost:8765', data=payload)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(
            "Anki is not reachable. Make sure Anki is running and configured to accept connections on 'http://localhost:8765'")
        sys.exit(1)


def main(deck_name):
    try:
        # Get the current working directory
        current_directory = os.getcwd()

        # Construct the path to the 'flashcards.json' file in the current directory
        json_file = os.path.join(current_directory, 'flashcards.json')

        # Read and preprocess the content of the JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            file_content = file.read()

        preprocessed_content = preprocess_json_content(file_content)
        flashcards = json.loads(preprocessed_content)

        # Save it back to a new JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, ensure_ascii=False, indent=2)

        print("Successfully cleaned JSON file.")

        # Create the deck if it doesn't exist
        create_deck(deck_name)

        # Add each flashcard to Anki
        for card in flashcards:
            question = card['question']
            answer = card['answer']
            result = add_note(question, answer, deck_name)
            if result['result']:
                print(f"Successfully added card with question: {question}")
            else:
                print(f"Failed to add card with question: {question}. Error: {result['error']}")

    except FileNotFoundError:
        print(
            "Error: 'flashcards.json' file not found in the current directory. Make sure the file exists and is in the same directory as the script.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSON for Anki flashcards.')
    parser.add_argument('deck_name', type=str, help='The Anki deck name to which cards should be added')

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.deck_name is None:
        print("Error: Please provide a deck name.")
        sys.exit(1)

    main(args.deck_name)

    input("Press Enter to exit...")  # Wait for user input to keep the console window open
