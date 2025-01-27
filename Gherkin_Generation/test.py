import pandas as pd
import json
import re
from crewai import Agent, Task, Crew, Process, LLM
import os

GEMINI_API_KEY=""

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
# Advanced configuration with detailed parameters
llm = LLM(
    model="gemini/gemini-1.5-pro-latest",
    temperature=0.7,        # Higher for more creative outputs
    max_tokens=4000,       # Maximum length of response
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

# Creating Feature Generation Agent
feature_generation_agent = Agent(
    role="Feature_generation_expert",
    goal="Generate features based on the provided system requirements.",
    backstory="""You are an expert in analyzing system requirements and identifying distinct features described within them.
                Your goal is to extract and organize features that are described in the requirements in a clear and structured manner.""",
    allow_delegation=False,
    max_iter=100,
    verbose=True,
    llm=llm
)

# Creating Scenario Generation Agent
scenario_generation_agent = Agent(
    role="Scenario_generation_expert",
    goal="Generate all possible scenarios for each identified feature.",
    backstory="""You are an expert in scenario analysis and generation. 
                 Given a list of features, your goal is to generate all potential scenarios, 
                 including edge cases and error handling scenarios, that are relevant for each feature.""",
    allow_delegation=False,
    max_iter=100,
    verbose=True,
    llm=llm
)

# Creating an agent to generate test cases 
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

# Creating a quality assurance expert which identifies missing test cases
quality_assurance_agent = Agent(
    role="Quality assurance expert",
    goal="""Identifying missing test cases in test coverage. 
            Review the original given text and the generated test cases.
            And generate the missing test cases.""",
    backstory="""You are a seasoned quality assurance expert. 
                 You have a deep understanding of industry regulations and use your analytical skills to design comprehensive test cases that uncover hidden bugs. 
                 You work closely with developers and testers to ensure that our software meets the highest quality standards.
                  """,
    allow_delegation=False,  
    max_iter =100,
    verbose=True,
    llm=llm
)

# Creating a traceability report generation expert for the test cases
tracebility_report_agent = Agent(
    role="Traceability report expert",
    goal="""Creating a traceability report by analyzing the requirements and test cases.""",
    backstory="""Deeply understanding and interpreting complex requirements, ensuring that each requirement is clearly defined and testable.
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
 
# Accessing user manual 
with open('ACCmanual.txt', 'r') as file:
    user_manual = file.read()

# Creating the task for requirement generation which is done by the requirement_generator agent
requirements = Task(
    description=f"""Following these guidelines, generate system requirements using the provided user manual {user_manual} in a clear and concise manner:

                    1. Identify each functionality and scenario described.
                    2. For each identified functionality, create a requirement with a unique identifier (e.g., REQ-001, REQ-002...).
                    3. Ensure requirements are phrased as clear and unambiguous statements using complete sentences.
                    4. Organize the requirements in an Excel file with columns: Requirement ID | Requirement Description

                    NOTE: Please generate the requirements based on the provided user manual only.
                    """,
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Requirement ID | Requirement Description

                        REQ-001 | <requirement1>
                        REQ-002 | <requirement2>
                           .
                           .
                           .
                            
                        IMPORTANT: Your response should be a valid Excel file (.xlsx).
                                   Your response must consist only of the table structure.
                                   Do not add any additional text, explanations, or summary lines before or after the table.
                                   The response should start with the header row and end with the last data row of the table.
                    """,
    output_file = "requirements3.csv",
    agent=requirement_agent
)


# Creating Task for Feature Generation from Requirements
feature_generation_task = Task(
    description=f"""Analyze the provided system requirements and generate a list of distinct features. Each feature should be clearly defined, unique, and relevant to the system being described.

                    Format your response as follows, where each feature is identified clearly:

                    Feature ID | Feature Description

                    FEATURE-001 | <feature1>
                    FEATURE-002 | <feature2>
                    .
                    .
                    .""",
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Feature ID | Feature Description
                        
                        FEATURE-001 | <feature1>
                        FEATURE-002 | <feature2>
                           .
                           .
                           .
                    IMPORTANT: Your response should be a valid Excel file (.xlsx).
                               Your response must consist only of the table structure.
                               Do not add any additional text, explanations, or summary lines before or after the table.
                               The response should start with the header row and end with the last data row of the table.
                    """,
    output_file="features3.csv",
    agent=feature_generation_agent,
    context=[requirements]
)

# Creating Task for Scenario Generation from Features
scenario_generation_task = Task(
    description=f"""For each feature identified in the previous task, generate all possible scenarios, including positive, negative, boundary, and edge cases.

                    Format your response as follows, where each scenario is described clearly for each feature:

                    Feature ID | Scenario ID | Scenario Description | Steps

                    FEATURE-001 | SCENARIO-001 | <scenario description> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                    FEATURE-002 | SCENARIO-001 | <scenario description> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                    .
                    .
                    .""",
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Feature ID | Scenario ID | Scenario Description | Steps
                        
                        FEATURE-001 | SCENARIO-001 | <scenario description> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                        FEATURE-002 | SCENARIO-001 | <scenario description> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                           .
                           .
                           .
                    IMPORTANT: Your response should be a valid CSV file (.csv) with pipe (|) delimiter.
                               Your response must consist only of the table structure.
                               Do not add any additional text, explanations, or summary lines before or after the table.
                               The response should start with the header row and end with the last data row of the table.
                    """,
    output_file="scenarios3.csv",
    agent=scenario_generation_agent,
    context=[feature_generation_task, requirements]
)

testcases = Task(
    description=f"""Based on the provided system requirements, generate comprehensive Gherkin test cases in a tabular format suitable for an Excel file with columns:

        Test Case ID | Feature | Scenario | Steps | Requirement ID
        TEST-001     | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <requirement_id> 
        TEST-002     | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <requirement_id> 
        .
        .
        .""",
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Test Case ID | Feature | Scenario | Steps | Requirement ID
                        
                        TEST-001 | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <requirement_id>
                        TEST-002 | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <requirement_id>
                           .
                           .
                           .
                    IMPORTANT: Your response should be a valid Excel file (.xlsx).
                               Your response must consist only of the table structure.
                               Do not add any additional text, explanations, or summary lines before or after the table.
                               The response should start with the header row and end with the last data row of the table.
                    """,
    output_file="testcases3.csv",
    agent=testcase_agent,
    context=[feature_generation_task,scenario_generation_task, requirements]
)

# Review by QA agent
quality_assurance_task = Task(
    description="""You are a Quality Assurance expert tasked with reviewing the test cases generated in the previous step.
                  Identify any missing test cases, edge cases, or boundary conditions that have not been covered by the previous set of test cases.
                  Review the test cases and generate the necessary additions, if any.
                  """,
    expected_output="""Provide a table with the missing test cases identified, if any.
                      The table should contain:
                      
                      Test Case ID | Feature | Scenario | Steps | Requirement ID
                      
                      TEST-003     | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result> | <requirement_id>
                      .
                      .
                      .
                      """,
    output_file="missing_test_cases3.csv",
    agent=quality_assurance_agent,
    context=[testcases,requirements]
)

# Traceability Report generation
traceability_report_task = Task(
    description="""Create a traceability report based on the test cases and requirements.
                  Generate a table that links each test case to its associated requirement and provides a clear mapping between the features, scenarios, and requirements.
                  Ensure that every requirement has at least one test case.
                  Format your report in an easy-to-read format that shows clear links between the requirements and the generated test cases.""",
    expected_output="""Format your report as a table:

                      Test Case ID | Requirement ID | Feature | Scenario | Steps
                      TEST-001     | REQ-001       | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                      TEST-002     | REQ-002       | <feature_name> | <scenario_name> | Given <precondition>\\nWhen <action>\\nThen <expected_result>
                      .
                      .
                      .
                      """,
    output_file="traceability_report3.csv",
    agent=tracebility_report_agent,
    context=[testcases, quality_assurance_task, requirements]
)


# #create the crew of all agents and tasks
# # Add Feature and Scenario Generation Tasks to Crew
# crew = Crew(
#     agents = [requirement_agent, feature_generation_agent, scenario_generation_agent, testcase_agent, quality_assurance_agent, tracebility_report_agent],
#     tasks = [requirements, feature_generation_task, scenario_generation_task, testcase_agent, quality_assurance_task, traceability_report_task],
#     process = Process.sequential,
#     full_output = True,
#     verbose = True
# )

# responses = crew.kickoff()

from crewai import Crew

# Make sure agents are instantiated properly and avoid any conflict with the configuration.
agents = [requirement_agent, feature_generation_agent, scenario_generation_agent, testcase_agent, quality_assurance_agent, tracebility_report_agent]

tasks = [requirements, feature_generation_task, scenario_generation_task, testcases, quality_assurance_task, traceability_report_task]

# Initialize the Crew object
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    full_output=True,
    verbose=True
)

# Kickoff the process
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


csv_to_excel("requirements3.csv", "requirements3.xlsx","|")
csv_to_excel("features3.csv", "features3.xlsx", "|")
csv_to_excel("scenarios3.csv", "scenarios3.xlsx", "|")
csv_to_excel("testcases3.csv", "testcases3.xlsx","|")
csv_to_excel("missing_test_cases3.csv", "missing_test_cases3.xlsx","|")
csv_to_excel("traceability_report3.csv", "traceability_report3.xlsx","|")









