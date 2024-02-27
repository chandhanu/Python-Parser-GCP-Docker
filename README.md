Introducing an advanced automated online service tool designed to streamline the process of dynamically correcting question papers for educators. This sophisticated tool leverages the power of Python programming language, incorporating Google Cloud Platform (GCP) OAuth tokens for secure access to Google Cloud-stored documents. Operating seamlessly within a Docker environment, this solution enhances efficiency and precision in the evaluation process by aligning with answer keys sourced from Google Docs. Its technical underpinnings ensure a robust and reliable performance, allowing educators to optimize their time and resources effectively.

ReadMe: 
-------
    1. Created user credentials in google cloud console and added service user credentials

    2. Developed a regex parser which uses regex to extract information 
        Limitations: 
        ------------
        a. Regex parser can only be text based documents 
        b. Regex is rule based, so the input should be structured 
            e.g. In the problem statement, "Questions (int): " is the only way to find beginning and ending of a question. And there is no way to identify answers uniquely especially is the questions and answers are multilined 
        c. Regex wont work on multimedia contents, if text are available after inbetween contents, regex does not capture the order of the content 
        -------> Completely created a new parser, this fetches metadata also 
        
    3. Developed a new parser to read the google doc from the two input files (QUestions Docs, Answers Docs ), which also preserves the structure, and collects meta data content by separating each questions and answers,
        a. This capture the order 
        b. This also can be extended to multimedia contents 

    4. Generated a nested dictionary dataype with Keys as Questions numbers and Value is also a dictionary with (Questions/Answers)
    Format {
        "0": {
            "q": ["\n", "Question 0: line11111111 \n", "Line333333\n", "Line2222222\n"],
            "a": ["Answers1\n", "Answers2\n", "\u000b\n", "Answers3\n"],
            "wc": 3
        }
    }
        Enhancements: 
        -------------
        a. The requirement was to export a "List" but I feel the usage of list strongly limits the usage of a data. I created a nested dictionary as shown above. 
        b. This can be easily accessed 
        c. Implementation is easier 
        d. Easier to visualize and understand in development point of view 
        e. The exported data also follows json format and used as a json file, this is easily integrated in cloud environment and REST
        d. This was it is easier to scale 

    5. Exported the data to final.json file, can be easily loaded into integration or with the same variable we can call automated grader

    6. Insert Word count to the inline for each student response in the google doc

    7. Displayed questions and answers in the terminal



References: 
-----------
1. https://developers.google.com/docs/api/how-tos/documents
2. https://developers.google.com/docs/api/how-tos/move-text
3. https://ericmjl.github.io/blog/2023/3/8/how-to-automate-the-creation-of-google-docs-with-python/

