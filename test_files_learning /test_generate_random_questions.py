import random
import string
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Docs API credentials
SERVICE_ACCOUNT_FILE = 'test-user-1.json'  

# Google Docs API and Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']

def authenticate():
    """
    Authenticates with the Google APIs using the provided service account credentials.
    """
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return docs_service, drive_service

def create_google_doc(docs_service, drive_service, folder_id):

    document = {
        'name': '2sigma-exam-1',
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.document'
    }

    # Create the Google Doc file
    response = drive_service.files().create(body=document).execute()
    doc_id = response['id']

    return doc_id

def populate_questions(doc_id, questions, answers):

    docs_service = authenticate()[0]

    requests = []
    index = 1

    for question_number, (question, answer) in enumerate(zip(questions, answers), start=1):
        requests.append(
            {
                'insertText': {
                    'location': {
                        'index': index
                    },
                    'text': f'Question {question_number}: {question}\n\n'
                }
            }
        )
        index += len(f'Question {question_number}: {question}\n\n')

        requests.append(
            {
                'insertText': {
                    'location': {
                        'index': index
                    },
                    'text': f'{answer}\n\n'
                }
            }
        )
        index += len(f'{answer}\n\n')

    batch_request = {
        'requests': requests
    }

    # Execute the batch update request to populate the Google Doc with questions and answers
    docs_service.documents().batchUpdate(documentId=doc_id, body=batch_request).execute()

def generate_random_questions(num_questions):

    questions = []
    for _ in range(num_questions):
        question_length = random.randint(10, 50)
        question = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=question_length))
        questions.append(question)
    return questions

def generate_random_answers(num_questions):
   
    answers = []
    for _ in range(num_questions):
        answer_length = random.randint(10, 30)
        answer = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=answer_length))
        answers.append(answer)
    return answers

def main():
    # Number of questions and folder ID
    num_questions = 3
    folder_id = '11MOSE8WsIO9CGP5Uq_yJtEzLd0AMIexy'  # Replace with the ID of your desired folder

    # Authenticate with Google APIs
    docs_service, drive_service = authenticate()

    # Generate random questions and answers
    questions = generate_random_questions(num_questions)
    answers = generate_random_answers(num_questions)

    # Create and populate Google Docs files
    for _ in range(num_questions):
        doc_id = create_google_doc(docs_service, drive_service, folder_id)
        populate_questions(doc_id, questions, answers)

if __name__ == '__main__':
    main()
