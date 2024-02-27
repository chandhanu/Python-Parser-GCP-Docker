import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import difflib
import copy 

def add_word_count_to_data(data):
    '''
    Module to count the WC in a multiple line questions 
    '''
    for qno, v in data.items():
        answers = v['a']
        answers = "".join(v['a'])
        word_count = len(answers.split())
        data[qno]['wc'] = word_count

    return data

def build_api_client(cred, scope):
    '''
    Module Define the credentials and API scope
    Set up authentication using the service account credentials
    '''
    credentials = service_account.Credentials.from_service_account_file(
        cred,
        scopes=scope
    )

    # Build the Google Docs API client
    service = build('docs', 'v1', credentials=credentials)

    return service

def create_question_value_pairs(q, a):

        '''
        Module to extract Questions and Answers 
        # TODO: 
        Multimedia contents 
        '''
        questions_data = {}
        answers_data = {}
        q_data = []
        for i in q:
            if 'textRun' in i['elements'][0]:
                q_content = i['elements'][0]['textRun']['content']
                #print(q_content,end="")
                q_data.append(q_content)
                #continue

        for i in q:
            if 'textRun' in i['elements'][0]:
                q_content = i['elements'][0]['textRun']['content']
                if "Question" in q_content:
                    a_data = []
                    for j in a:
                        if 'textRun' in j['elements'][0]:
                            answer_content = j['elements'][0]['textRun']['content']
                            
                            if answer_content in q_content or q_content in answer_content: # To handle multiple line questions 
                                if j['elements'][0]['textRun']['content'] != '\n':
                                    questions_data[q.index(i)] = q_content
                                    #print(q_content)
                            else:
                                if answer_content != '\n' and answer_content not in " ".join(q_data):
                                    #print(answer_content)
                                    answers_data[q.index(i)] = answer_content
                                    a_data.append(answer_content)

        return q_data, a_data


def display_dict(data):
    '''
    Utility module to visualize the raw data with ease
    '''
    print(json.dumps(data, indent=3))

def display_questions(questions):
    '''
    Module to print questions 
    '''
    for question_number, question_text in questions.items():
        print(f"Question {question_number}: {question_text}")
        print('-'*20)

def display_questions_n_answers(questions_n_answers):
    '''
    Utility function to print the Questions and Answers
    '''
    print("*************************")
    print("********* Q & A *********")
    print("*************************\n")
    for k,v in (questions_n_answers).items():
        #print("Question",k,":")
        print("".join(v["q"]).strip('\n'))
        print("---------------"*5)
        print("Answers :")
        print("".join(v["a"]).strip('\n'))
        print("---------------"*5)

def display_word_count(data):
    for qno, v in data.items():
        print("Question :", qno, "WordCount :", v["wc"])

def dump_json(data, json_file):
    '''
    Utility module to export Google doc content to viewable json format
    '''
    # Open a file in write mode
    with open(json_file, "w") as file:
        # Write the JSON data to the file
        json.dump(data, file)

def extract_answers(questions, answers):
    '''
    Module to parser using extracted questions and newly parsed answers
    '''
    diff = difflib.unified_diff(questions.splitlines(), answers.splitlines(), lineterm='')
    
    differences = []
    
    for line in diff:
        line = line.strip()
        if line.startswith('+') and len(line)>1:
            line = line[1:]
            line = "".join(line.rstrip('\n'))

            differences.append(line)
            differences.append('\n')
    differences.remove("++")
    
    return differences

def get_document_content(service, doc_id):

    '''
    Module to load and get the content
    '''
    document = service.documents().get(documentId=doc_id).execute()
    content = document['body']['content']

    return content

def parse_question(content):
    '''
    Module to parse the multiple line questions
    Logic : use regex expressions to match

    # TODO: Parse different type of questions
    '''
    questions = {}
    question_pattern = r"Question (\d+): (.+?)(?=Question \d+|$)"
    text = ''

    for elements in content:
        if 'paragraph' in elements:
            paragraph = elements['paragraph']
            for element in paragraph['elements']:
                    text += element['textRun']['content']

    matches = re.findall(question_pattern, text, re.DOTALL)

    for match in matches:
        question_number = int(match[0])
        question_text = match[1].strip()
        questions[question_number] = question_text    

    return questions

def extract_elements_by_question(content):
    '''
    Module to seperate questions - the meta data of a question is stored in a 
    key/value pair with key being the question number and value being the meta-data 
    '''
    qno=0
    meta_data={}
    for elements in content:
        if 'paragraph' in elements:
            paragraph = elements['paragraph']
            for element in paragraph['elements']:
                if "textRun" in element:
                    if "Question" in element['textRun']['content']:
                        word = element['textRun']['content'].strip().split(':')
                        qno = int(word[0].split(' ')[1]) #extracting qno
                        meta_data[int(qno)] = [] # initialize the list of elemenets to be stored 
                        meta_data[qno].append(paragraph) #append elements to the list
                    elif qno in meta_data:
                        meta_data[qno].append(paragraph)
        
    return meta_data  


def parse_questions_n_answers(question_content, answer_content):
    

    questions_meta_data=extract_elements_by_question(question_content)
    #print('Questions:::\n',json.dumps(questions_meta_data[4], indent = 3))

    answers_meta_data=extract_elements_by_question(answer_content)
    #print("Answers::::\n",json.dumps(answers_meta_data[4], indent = 3))
    
    #dump_json(questions_meta_data, "q_meta_data.json")
    #dump_json(answers_meta_data, "a_meta_data.json")
    
    qna_data = {}
    questions_list, answers_list = None, None
    for qno in questions_meta_data.keys():

        q,a = questions_meta_data[qno], answers_meta_data[qno]
        questions_list,answers_list = create_question_value_pairs(q,a)
        #questions_list,answers_list = create_question_value_pairs(q,a)

        qna_data[qno] = {
            'q':list(set(questions_list)),
            'a':list(set(answers_list))
        }

    
    return qna_data, questions_meta_data, answers_meta_data


def insert_word_count(service, document_id, questions_n_answers):

    '''
    Module to insert word count line for each students responses 
    Challenges: 
        The moving index problem - Once a line is insert at the top, the corresponding 
        (startindex, endindex) is also updated on all following elements in the google doc 
    
    Logic: 
        The logic is based on the recommended method by google, by following UTF encoding for google docs and insert the word count from bottom to top. In this way, the moving index problem is taken care. 
        To Achieve this, the Content and the parsed QnA is reversed. 
    '''
    # Reversing the contents of processed meta-data
    reversed_dict = {}
    rkeys = list(questions_n_answers.keys())[::-1]
    for k in rkeys:
        reversed_dict[k] = questions_n_answers[k]
    

    #display_dict(reversed_dict)

    document = service.documents().get(documentId=document_id).execute()


    for k,v in (reversed_dict).items():
        questions_full = " ".join(v["q"]).strip('\n')
        answers_full = " ".join(v["a"]).strip('\n')

        reverse_answers = []
        dict1 = {}
        requests = []

        # service = build_api_client(cred= test_cred, scope=scope)
        # document = service.documents().get(documentId=document_id).execute()

        for element in reversed(document['body']['content']):
            if 'paragraph' in element and 'textRun' in element['paragraph']['elements'][0]:
                text = element['paragraph']['elements'][0]['textRun']['content']
                if text == "\n" :#or text in questions_full:
                    continue
                if text in v['a']:
                    v['a'].remove(text)
                    reverse_answers.insert(0, text)
                    continue
                
                if len(reverse_answers) ==0:
                    continue
            
                if len(reverse_answers) == v['wc'] or len(reverse_answers) == len(answers_full.split()) or len(v['a'])==0 and k not in dict1 :

                    dict1[k]= 0
                    word_count = v['wc']
                    
                    requests.append({
                        'insertText': {
                            'location': {
                                'index': element['endIndex']
                            },
                            'text': f'\nWord Count: {word_count}\n',
                        }
                    })
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': element['endIndex'],
                                'endIndex': element['endIndex'] + len(f'\nWord Count: {word_count}') # Modifying the index generated to update end index
                            },
                            'textStyle': {
                                'foregroundColor': {
                                    'color': {
                                        'rgbColor': {
                                            'red': 1.0,
                                            'green': 0.0,
                                            'blue': 0.0
                                        }
                                    }
                                }
                            },
                            'fields': 'foregroundColor',
                        }
                    })

                    
                    
                    
                    batch_request = service.documents().batchUpdate(
                        documentId=document_id, body={'requests': requests}
                    )
                    batch_request.execute()

                    print("Word count inserted for Quesition :", k)
                    
        
    if len(requests) == 0:
        print(" Error: No Requests added ")   
        exit()

    print("Word count inserted successfully.")


       

def main():


    TEST_CRED = 'credentials/test-user-1.json' #Service Account with 
    SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
    
    #Others Two files 
    #QUESTION_DOC_ID = '1D2U20bSfeT35fukuUreJ8dWY_7HNOxPdCyEke9naMNo'
    #ANSWER_DOC_ID = '1q00mIG4OcscyqkjEe6FA4TDBZvJXCWWRW9-osnYZKjI'

    QUESTION_DOC_ID = '1ZEi7KBMCj_JMxoCNS92WSHQYtuBUr0FEYgz3cKuy-Eg'
    ANSWER_DOC_ID = '19ne3LqvdYs2NaEuKoKqMFVBG-e_Pruvr3PEmp50iiQ0'
    SERVICE = None
    SERVICE = build_api_client(cred= TEST_CRED, scope=SCOPE)
    
    QUESTIONS_CONTENT = get_document_content(service=SERVICE, doc_id=QUESTION_DOC_ID)


    ANSWERS_CONTENT = get_document_content(service=SERVICE, doc_id=ANSWER_DOC_ID)
    data, qmd, amd = parse_questions_n_answers(QUESTIONS_CONTENT,ANSWERS_CONTENT)

    data_with_wc = add_word_count_to_data(data)

    #data_with_wc = add_word_count_to_data(data)

    backup_data = copy.deepcopy(data_with_wc)
    dump_json(data_with_wc, "Exported_data.json")
    insert_word_count(SERVICE, ANSWER_DOC_ID ,data_with_wc)

    display_questions_n_answers(backup_data)


if __name__ == "__main__":
    main()
    '''
    Logical Improvements : 
    ----------------------
    1. Structured formate for Questions and Answers, Questions can be taken from DB, Answers can be stored in DB 
        - use case : Questions can be easily parsed, provides more flexibility 
    2. Use Template engine, to be passed on to end document 
        - use case : generate Questions from DB/spreadsheet
    3. Generate PDF report for the evaluation of the answers given by the student with feedback 
        - use case : automated feedback with course contents may be with explanations
    4. Preparing Cheat sheet depending on the complexity of the exam like formulae sheet 
    5. 

    Implementational Improvements : 
    -------------------------------
    1. Word count after word count counting extra word counts 
    2. Data with pics and tables - data is collected - have to store it in the right questions
    3. Generating Exam name, student's info ID/Name, Course Code, etc... 
    '''

