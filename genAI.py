import json
import openai
import sys
import config

openai.api_key = config.OPENAI_API_KEY

STANDARDS = {
    "CCSS.ELA-LITERACY.W.4.9": "CCSS.ELA-LITERACY.W.4.9 - Draw evidence from literary or informational texts to support analysis, reflection, and research."
}

def run_interactive():
    print("\n")
    theme = input("Please enter the theme:")
    i = 0
    print("\n")
    print("Here are the available standards:")
    keys = []
    for s in STANDARDS.keys():
        i += 1
        keys.append(s)
        print(i, ":", s)
    cc_standard = ""
    while cc_standard == "":
        cc_standard_input = input(f"Please select a standard [1-{i}]:")
        try:
            choice = int(cc_standard_input)        
        except:
            continue
        if choice > 0 and choice <= i:
            cc_standard = STANDARDS[keys[choice-1]]            

    print("\nTheme:")
    print (theme)
    print("\nStandard:")
    print (cc_standard)
    
    messages = generate_question_messages(cc_standard, theme)
    print("\nGettig question...")
    response = get_response(messages)

    message = response["choices"][0]["message"] 
    messages.append(message)
    content = json.loads(response["choices"][0]["message"]["content"])
    print ("\nContext:")
    print (content["context"])
    print ("\nQuestion:")
    print (content["question"])
    print ("\nEvaluation:")
    print (content["evaluation"])

    

def get_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    return response


def generate_question_messages(cc_standard, theme):
    return [
        {"role": "system", "content": """
Use the following step-by-step instructions to respond to user inputs. The user is a grade-school teacher and will provide a common core education standard and a theme. The standard and the theme will be in quotes, separated by a comma. You will provide the teacher with the information necessary to evaluate a student against the standard.
Provide the response content in JSON format.
Step 1 - Use the provided theme to randomly select a topic and generate context material about which a student could answer questions. Use the vocabulary and syntax of the standard's target grade level. Use the key "context" for this JSON object.
Step 2 - Generate a free-response question that can be answered by reading the context that will test the common core standard. Use the vocabulary and syntax of the standard's target grade level. Use the key "question" for this JSON object.
Step 3 - Generate an evaluation rubric based on the context. Use a scale from 4 points (best) to 0 points (worst). Use the key "evaluation" for this JSON object with numeric score amd text description key value pairs.
Repeat the previous steps to produce different contexts and questions. 
        """},
        {"role": "user", "content": f"\"{cc_standard}\",\"{theme}\""},
    ]


def generate_evaluation_messages(cc_standard, theme, content, answer):
    content["standard"]=cc_standard
    content["theme"]=theme
    content["answer"]=answer
    return [
        {
            "role": "system",
            "content": f"""
The user is a grade-school teacher and will provide a JSON object containing the following:
- A common core education standard with key "standard"
- The theme of the standard with the key "theme"
- A question with key "question"
- A student's answer to the question with the key "answer"
- The context necessary to answer the question with key "context"
- An evaluation rubric to score the answer with the key "evaluation"
Evaluate the student's answer based solely on the information provided in the context. 
Do not consider any additional knowledge or information about the theme of {theme}.
Respond in JSON format with the following:
- The numeric score from the evaluation. Use the key "score"
- The rubric description assigned to the score. Use the key "detail"
- Provide details about how you arrived as the score. Use the key "commentary"
            """
        },
        {
              "role": "user",
              "content": json.dumps(content)
        },
        {
              "role": "user",
              "content": f"""
Evaluate the student's answer based solely on the rubric and information provided in the context. 
Do not consider any additional knowledge or information about the theme of {theme}."""
        }
    ]