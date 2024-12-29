import time
import pandas as pd
import json
import re


from crewai import Agent, Task, Crew, Process 

# Importing the llm model
from langchain_google_genai import ChatGoogleGenerativeAI 

# Instantiate the llm
llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        verbose=True,
        temperature=0.1,
        max_tokens=100,
        google_api_key="AIzaSyCj0a6TbRWXuJkdZukbJDnBb7MKbv6Ikd8"
    )

requirement_agent = Agent(
    role="Requirements_generator",
    goal="Generate comprehensive system requirements.",
    backstory="""You are expert in reading and understanding technical documantation and can extract testable requirements from user manual.
                You are highly skilled and experienced requirements engineer, specializing in crafting precise and exhaustive requirements for software systems.
                You have a deep understanding of user manuals and can extract essential information to create a comprehensive set of requirements for testing.
                You will carefully consider all relevant aspects of the user manual to generate a comprehensive set of requirements that cover all possible scenarios and contingencies.
                """,
    allow_delegation=False,
    max_iter =100,
    verbose=True,   
    llm=llm
)

#creating an agent to genearate test cases 
testcase_agent = Agent(
    role="Test case generator",
    goal="""Generate the Gherkin test cases based on the extracted requirements""",
    backstory="""You are a highly skilled and experienced test case generation expert,
                 You possess a deep understanding of software testing methodologies and have a keen eye for identifying potential defects,
                 Given a clear and concise description of a system or feature,
                 You can generate a robust set of test cases that cover a wide range of scenarios, including positive, negative, boundary, and edge cases.
                 You am proficient in various testing techniques such as functional testing, integration testing, and system testing. 
                 You goal is to help ensure the quality and reliability of software applications by providing thorough and effective test cases.
                 """,
    allow_delegation=False,
    max_iter =100,
    verbose=True,
    llm=llm
)

#Creating a quality assurance expert which identifying missing test case
quality_assurance_agent = Agent(
    role="Qaulity assurance expert",
    goal="""identifying missing test cases in test coverage. 
            Review the original given text and the generated test cases.
            And generate the missing test cases.""",
    backstory="""you a seasoned quality assurance expert. 
                 you have a deep understanding of industry regulations and use my analytical skills to design comprehensive test cases that uncover hidden bugs. 
                 You work closely with developers and testers to ensure that our software meets the highest quality standards.
                  """,
    allow_delegation=False,  
    max_iter =100,
    verbose=True,
    llm=llm
)

#creating a traceability report generation expert of the test cases
tracebility_report_agent = Agent(
    role=" tracebility report expert",
    goal="""Creating a traceability report by Analyzing the requirements and test cases.""",
    backstory="""Deeply understanding and interpreting complex requirements , ensuring that each requirement is clearly defined and testable.
                Establishing clear and logical connections between requirements and test cases, ensuring that all aspects of the requirements are adequately covered.
                Identifying any discrepancies or omissions between requirements and test cases, ensuring that the testing process is thorough and complete.
                Developing comprehensive traceability matrices that clearly demonstrate the relationship between requirements and test cases, providing a visual representation of test coverage.
                Following established quality standards and best practices in the automotive industry, ensuring that the traceability report meets the highest quality standards.
                The expert has a proven track record of delivering high-quality traceability reports that have contributed to the successful development and testing of numerous automotive products. 
                 """,
    allow_delegation=False,
    max_iter =100,
    verbose=True,
    llm=llm
)
 
#Accessing user manual 
with open('ADASmanual.txt','r') as file:
    user_manual = file.read()

#creating the task for requirement generation which is done by requirement_generator agent
requirements = Task(
    description=f"""Following these guidelines,to generate system requirements using provided user manual   {user_manual} in a clear and concise manner:

                    1. Identify each functionality and scenario described.
                    2. For each identified functionality, create a requirement with a unique identifier (e.g., REQ-001, REQ-002...).
                    3. Ensure requirements are phrased as clear and unambiguous statements using complete sentences.
                    4. Organize the requirements in an Excel file with columns: Requirement ID | Requirement Description

                    NOTE : Please generate the requirements based on the provided user manual only.
                    """,
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Requirement ID | Requirement Description

                        REQ-001 | <requirment1>
                        REQ-002 | <requirment2>
                           .
                           .
                           .
                            
                        IMPORTANT: Your response should be a valid Excel file (.xlsx).
                                   Your response must consist only of the table structure.
                                   Do not add any additional text, explanations, or summary lines before or after the table.
                                   The response should start with the header row and end with the last data row of the table.
                    """,
    output_file = "requirements.csv",
    agent=requirement_agent
)

testcases = Task(
    description=f"""Based on the provided system requirements, generate comprehensive Gherkin test cases in a tabular format suitable for an Excel file with columns:

        Test Case ID | Feature | Scenario | Steps | Requirement ID

        Focus on Edge Cases: Include test cases that cover potential edge cases and error handling scenarios.

        Clear Descriptions: Write concise and informative test case descriptions that clearly describe the test objective.

        Validity Check: Ensure each test case is valid and adequately tests its associated requirement.
        """,
    expected_output="""Format your response as if you were describing the contents of an Excel file:

        Test Case ID | Feature | Scenario | Steps | Requirement ID
        TC-001 | Feature: <feature_name> | Scenario: <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <REQ_ID>
        TC-002 | Feature: <feature_name> | Scenario: <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <REQ_ID>
        ...

        Note: Use \\n for line breaks within the Steps column to separate Given/When/Then.
        IMPORTANT: Your response should be a valid CSV file (.csv) with pipe (|) delimiter.
        Your response must consist only of the table structure.
        Do not add any additional text, explanations, or summary lines before or after the table.
        The response should start with the header row and end with the last data row of the table.
        """,
    output_file="testcase.csv",
    agent=testcase_agent,
    context=[requirements]
)



missing_testcases = Task(
    description = f"""Review the requiremts and generated test cases carefully:

        Your task:
        1. Analyze the generated test cases.
        2. Identify any functionalities, scenarios, or edge cases that are not covered in the test cases.
        3. For each missing scenario, create a new Gherkin test case using the following format and format your response as a CSV-like structure with the following columns, separated by pipes (|):

        Missing Test Case ID | Feature | Scenario | Steps | Req ID

        Where:
        - Missing Test Case ID: Use the format MTC-[number]
        - Feature: Give a descriptive name to feature.
        - Scenario: Give a descriptive name to scenario.
        - Steps: Given <precondition>\\nWhen <action>\\nThen <expected_result>
        - Req ID: If applicable, reference the requirement ID from the original text that this test case addresses
        
        4. Ensure each new test case addresses a unique scenario not covered in the original set.
        """,
    expected_output = """Output your findings in a tabular format that resembles an Excel spreadsheet,
        with the headers "Missing Test Case ID", "Feature","Scenario", "Steps", and "Req ID".
        Each row should represent a new test case.

         Example output format:

        Missing Test Case ID | Feature | Scenario | Steps | Req ID
        MTC-001 | Feature: <feature_name> | Scenario: <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | [Req ID if applicable]
        MTC-002 | Feature: <feature_name> | Scenario: <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | [Req ID if applicable]
        ...

        IMPORTANT: Your response should be a valid CSV file (.csv) with pipe (|) delimiter.
        Your response must consist only of the table structure.
        Do not add any additional text, explanations, or summary lines before or after the table.
        The response should start with the header row and end with the last data row of the table.
        """,
    output_file = "missing_testcases.csv",
    agent=quality_assurance_agent,
    context=[testcases]

)

traceability_report = Task(
    description = """creating a traceability report by analyzing the sets of requirements and test cases for ADAS.
        1. Create a comprehensive traceability report that links each test case to its corresponding requirement.
        2. Evaluate if each test case is valid and adequately tests its associated requirement.
        3. Verify that all test cases are correctly mapped to their corresponding requirements.
        4. Format your response as a CSV-like structure with the following columns, separated by pipes (|):
            
            Rquipurement ID|Requirement Description|Test Case ID|Feature|Scenario|Steps|Validity|Comments

        5. Ensure all test cases from both sets are included and evaluated.
        6. Use clear, concise language in your descriptions and comments.
        7. Start your response with the header row.
        """,
    expected_output = """Output your findings in a tabular format that resembles an Excel spreadsheet,
            Each row should represent a new test case.

             Example format:
            Requirement ID|Requirement Description|Test Case ID|Feature|Scenario|Steps|Validity|Comments

            REQ-001|<requirement description>|TC-001|<feature_name>|<scenario_name>|Given <precondition>\\nWhen <action>\\nThen <expected_result>|<valid/invalid>|<comment>
            REQ-001|<requirement description>|TC-002|<feature_name>|<scenario_name>|Given <precondition>\\nWhen <action>\\nThen <expected_result>|<valid/invalid>|<comment>
            ...

            REQ-002|<requirement description>|TC-001|<feature_name>|<scenario_name>|Given <precondition>\\nWhen <action>\\nThen <expected_result>|<valid/invalid>|<comment if invalid else N/A>
            REQ-002|<requirement description>|TC-002|<feature_name>|<scenario_name>|Given <precondition>\\nWhen <action>\\nThen <expected_result>|<valid/invalid>|<comment if invalid else N/A>
            ...

            Provide your traceability report in this exact format, ensuring each row is on a new line.
            IMPORTANT: Your response should be a valid  CSV file (.csv) with pipe (|) delimiter.
            Your response must consist only of the table structure.
            Do not add any additional text, explanations, or summary lines before or after the table.
            The response should start with the header row and end with the last data row of the table.

            """,
    output_file = "traceability_report.csv",
    agent = tracebility_report_agent,
    context = [requirements,testcases,missing_testcases]
)

regenerated_testcases = Task(
    description = f"""Review the traceability report and regenerate the test cases which are invalid:

        Your task:
        1. Analyze both the original text and the generated invalid test cases.
        3. For each invalid test case, create a new test case using the following format:

        Regenerated Test Case ID | Feature | Scenario | Steps | Req ID

        Where:
        - Regenerated Test Case ID: Use the format RTC-[number]
        - Feature: Give a descriptive name to feature.
        - Scenario: Give a descriptive name to scenario.
        - Steps: Given <precondition>\\nWhen <action>\\nThen <expected_result>
        - Req ID: If applicable, reference the requirement ID from the original text that this test case addresses

        4. Ensure each new test case addresses a unique scenario not covered in the original set.
        """,
    expected_output = """Output your findings in a tabular format that resembles an Excel spreadsheet,
        with the headers "Regenerated Test Case ID", "Feature","Scenario", "Steps", and "Req ID".
        Each row should represent a new test case.

         Example output format:

        Regenerated Test Case ID | Feature | Scenario | Steps | Req ID
        RTC-001 | Feature: <feature_name> | Scenario: <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | [Req ID if applicable]""",
    output_file = "traceability_report.csv",
    agent = tracebility_report_agent,
    context = [requirements,testcases,missing_testcases]
)

regenerated_traceability_report = Task(
    description = """regenerate traceability report by analyzing the sets of requirements and traceability report and regenerated testcases.
                      1. Create a comprehensive traceability report that links each test case to its corresponding requirement.
                      2. Evaluate if each test case is valid and adequately tests its associated requirement.
                      3. Verify that all test cases are correctly mapped to their corresponding requirements.
                      4. Format your response as a CSV-like structure with the following columns, separated by pipes (|):
                         
                         Rquipurement ID|Requirement Description|Test Case ID|Test Case Description|Validity|Comments

                      5. Ensure all test cases from both sets are included and evaluated.
                      6. Use clear, concise language in your descriptions and comments.
                      7. Start your response with the header row.
                      8. Replace the invalid test cases with newly generated testcases 
                   """,
    expected_output = """Output your findings in a tabular format that resembles an Excel spreadsheet,
                         Each row should represent a new test case.

                         Example format:
                         Requirement ID|Requirement Description|Test Case ID|Test Case Description|Validity|Comments

                         REQ-001|<requirement description>|TC-001|<test case description>|<valid/invalid>|<comment>
                         REQ-001|<requirement description>|TC-002|<test case description>|<valid/invalid>|<comment>
                                                             .
                                                             .
                                                             .

                         REQ-002|<requirement description>|TC-001|<test case description>|<valid/invalid>|<comment if invalid else N/A>
                         REQ-002|<requirement description>|TC-002|<test case description>|<valid/invalid>|<comment if invalid else N/A>
                                                             .
                                                             .
                                                             .
                                                            
                            .
                            .
                            .

                         Provide your traceability report in this exact format, ensuring each row is on a new line.
                         IMPORTANT: Your response should be a valid  CSV file (.csv).
                                   Your response must consist only of the table structure.
                                   Do not add any additional text, explanations, or summary lines before or after the table.
                                   The response should start with the header row and end with the last data row of the table.

                    """,
    output_file = "regenerated_traceability_report.csv",
    agent = tracebility_report_agent,
    context = [requirements,missing_testcases,traceability_report,regenerated_testcases]
)


#create the crew of all agents and tasks
crew = Crew(
    agents = [requirement_agent,testcase_agent,quality_assurance_agent,tracebility_report_agent],
    tasks = [requirements,testcases,missing_testcases,traceability_report,regenerated_testcases,regenerated_traceability_report],
    process = Process.sequential,
    full_output = True,
    verbose = True
)

responses = crew.kickoff()


def csv_to_excel(csv_file, excel_file,delimiter):
    """Converts a CSV file to an Excel file using pandas.

    Args:
        csv_file (str): Path to the CSV file.
        excel_file (str): Path to the output Excel file.
    """

    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file,delimiter=delimiter)
        df = df.iloc[:, 1:-1]
        # Write the DataFrame to an Excel file
        df.to_excel(excel_file, index=False)

        print("Conversion successful!")
    except Exception as e:
        print(f"Error occurred during conversion: {e}")


csv_to_excel("requirements.csv", "requirements.xlsx","|")
csv_to_excel("testcase.csv", "testcase.xlsx","|")
csv_to_excel("missing_testcases.csv", "missing_testcases.xlsx","|")
csv_to_excel("traceability_report.csv", "traceability_report.xlsx","|")
csv_to_excel("regenerated_testcases.csv", "regenerated_testcases.xlsx","|")
csv_to_excel("regenerated_traceability_report.csv", "regenerated_traceability_report.xlsx","|")













