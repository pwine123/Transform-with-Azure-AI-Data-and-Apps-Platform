
from promptflow.core import tool
import os
from datetime import datetime
import json

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(question_list_json: str) -> str:
    # write the question list to a jsonl file
    # Define the folder name
    folder_name = "./output"

    # Check if the folder exists
    if not os.path.exists(folder_name):
        # If it does not exist, create the folder
        os.makedirs(folder_name)
    # Generate a filename with a date stamp
    filename = "output/question_list_{}.jsonl".format(datetime.now().strftime("%Y%m%d%H%M%S"))
    
    # Check if the file exists
    if os.path.exists(filename):
        # If it exists, delete the file
        os.remove(filename)
    
    question_list = json.loads(question_list_json)

    # Proceed to use the file with the new name
    with open(filename, "w") as f:
        for question in question_list["questions"]:
            json_record = json.dumps(question)
            f.write(json_record + "\n")
            
