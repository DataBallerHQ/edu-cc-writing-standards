import genai
import json
import sys
import time
import threading
import textwrap
import random

def spinner(spinning_container):
    while spinning_container[0]:
        for char in "|/-\\":
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b \b")

def print_section(header, content):
    print(f"\n{header}:")
    wrapped_text = textwrap.fill(content, width=80)
    print(wrapped_text)

def get_inputs():
    i = 0
    print("Available Common Core standard: ")
    keys = []
    for s in genai.STANDARDS.keys():
        i += 1
        keys.append(s)
        print(i, ":", s)
    cc_standard = ""
    while cc_standard == "":
        cc_standard_input = input(f"\nPlease select a standard [1-{i}]:")
        try:
            choice = int(cc_standard_input)        
        except:
            continue
        if choice > 0 and choice <= i:
            cc_standard = genai.STANDARDS[keys[choice-1]]            

    theme = ""
    while theme == "":
        theme = input("Please enter the theme: ")
    
    return cc_standard, theme

def automate_tests(question_count, answer_count):
    cc_standard, theme = get_inputs()
    test_results = {
        "standard": cc_standard,
        "theme": theme,
        "questions": [],
    }
    q_messages = genai.generate_question_messages(cc_standard, theme)
    for i in range(question_count):
        print(f"Generating question {i+1}...")
        response = genai.get_model_response(q_messages)
        q_content = json.loads(response["choices"][0]["message"]["content"])
        q_messages.append({"role": "assistant", "content": json.dumps(q_content)})
        test_results["questions"].append({
            "context": q_content["context"],
            "question": q_content["question"],
            "evaluation": q_content["evaluation"],
            "answers": []
        })
        random_target = int(random.randint(0, 4))
        a_messages = genai.generate_ai_answers_message(q_content, random_target)
        for j in range(answer_count):
            print(f"Generating answer {j+1}...")
            random_target = int(random.randint(0, 4))
            response = genai.get_model_response(a_messages, temperature=1)
            answer = response["choices"][0]["message"]["content"]
            a_messages.append({"role": "assistant", "content": answer})

            print(f"Generating evaluations {j+1}...")
            messages = genai.generate_evaluation_messages(cc_standard, theme, q_content, answer)
            response = genai.get_model_response(messages)
            a_content = json.loads(response["choices"][0]["message"]["content"])
    
            test_results["questions"][i]["answers"].append({
                "answer": answer,
                "target": random_target,
                "score": a_content["score"],
                "detail": a_content["detail"],
                "commentary": a_content["commentary"]
            })

    # Open a file for writing
    filename = cc_standard.replace(".", "_").replace(" ", "_").lower() + "_tests.json"
    with open(filename, 'w') as file:
        json.dump(test_results, file)

    print("Tests complete. Results saved to", filename)


def start():
    
    test_mode = input("Run automated test mode? [y/n]: ")
    if test_mode.lower() == "y":
        print("TEST MODE\n")
        question_count = int(input("How many questions? "))
        answer_count = int(input("How many answers per question? "))
        automate_tests(question_count, answer_count)  

    else:
        print("INTERACTIVE MODE\n")
        cc_standard, theme = get_inputs()

        while True:

            print_section("Standard", cc_standard)
            print_section("Theme", theme)

            print("\nGenerating question...")
            # Start the spinner
            spinning_container = [True]
            spinner_thread = threading.Thread(target=spinner, args=(spinning_container,))
            spinner_thread.start()

            # Generate question
            messages = genai.generate_question_messages(cc_standard, theme)
            response = genai.get_model_response(messages)
            q_content = json.loads(response["choices"][0]["message"]["content"])

            # Stop the spinner
            spinning_container[0] = False
            spinner_thread.join()
            print("Ready. Please answer the following question:")

            print_section("Context", q_content["context"])  
            print_section("Question", q_content["question"])

            print("")
            answer = ""
            while answer == "":
                answer = input("Answer: ")

            print("\nEvaluating answer...")
            # Start the spinner
            spinning_container = [True]
            spinner_thread = threading.Thread(target=spinner, args=(spinning_container,))
            spinner_thread.start()

            # Generate evaluation
            messages = genai.generate_evaluation_messages(cc_standard, theme, q_content, answer)
            response = genai.get_model_response(messages)
            a_content = json.loads(response["choices"][0]["message"]["content"])

            # Stop the spinner
            spinning_container[0] = False
            spinner_thread.join()
            print("Ready. Please review the evaluation:")

            print_section("Score", str(a_content["score"]))
            print_section("Detail", a_content["detail"])
            print_section("Commentary", a_content["commentary"])
            print("\nEvaluation Rubric:")
            for k,v in q_content["evaluation"].items():
                content = f"[{k}]: {v}"
                print(textwrap.fill(content, width=60))
            print("")

            another = input("Answer another question? [y/n]: ")
            if another.lower() != "y":
                break        

start()