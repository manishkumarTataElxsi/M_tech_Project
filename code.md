!pip install crewai crewai_tools


from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import (PDFSearchTool)

import pandas as pd
import json
import re
from crewai import Agent, Task, Crew, Process, LLM
import os

!pip install PyPDF2  # Install the PyPDF2 library



import PyPDF2

def read_full_pdf(pdf_path):
  """Reads the entire content of a PDF file into a single string.

  Args:
    pdf_path: The path to the PDF file.

  Returns:
    A string containing the full content of the PDF.
  """

  with open(pdf_path, 'rb') as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    full_text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        full_text += page.extract_text()  # Accumulate text from all pages

    return full_text

# Example usage:
pdf_path = '/content/EVOQUE-HANDBOOK.pdf'  # Replace with your PDF path
full_pdf_content = read_full_pdf(pdf_path)




# Advanced configuration with detailed parameters
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.3,        # Higher for more creative outputs
    max_tokens=32000,       # Maximum length of response
)


requirement_agent = Agent(
    role="Requirements_generator",
    goal="Extract comprehensive system requirements.",
    backstory="""You are expert in reading and understanding technical documantation and can extract testable requirements from Software Requirement Specifications(SRS) file.
                You are highly skilled and experienced requirements engineer, specializing in crafting precise and exhaustive requirements for software systems.
                You have a deep understanding of  Software Requirement Specifications(SRS) and can extract essential information to create a comprehensive set of requirements for testing.
                You will carefully consider all relevant aspects of the  Software Requirement Specifications(SRS) to extract a comprehensive set of requirements.
                """,
    #tools = [tool],
    allow_delegation=False,
    max_iter =100,
    verbose=True,
    llm=llm
)

# Creating Feature Generation Agent
feature_generation_agent = Agent(
    role="Feature_generation_expert",
    goal="Generate features for Behavior-Driven Development based on the provided system requirements.",
    backstory="""You are an expert in analyzing system requirements and identifying distinct features described within them.
                Your goal is to extract and organize features for Behavior-Driven Developmen that are described in the requirements in a clear and structured manner.""",
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
                 Given a list of features, your goal is to generate all potential scenarios for each feature,
                 including edge cases and error handling scenarios, that are relevant for each feature.
                 The scenarios should ve realistic, comprehensive, and effective for testing and validation.""",
    allow_delegation=False,
    max_iter=100,
    verbose=True,
    llm=llm
)

# Creating an agent to generate test cases
testcase_agent = Agent(
    role="Test case generator",
    goal="""Generate the Gherkin test cases for Behavior-Driven Developmen based on the extracted features , Scenarios from requirements""",
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

# Creating an agent to convert features into Python scripts using Behave
behave_script_agent = Agent(
    role="Behave Script Generator",
    goal="Generate Python scripts for Behavior-Driven Development using the Behave library based on the provided features and scenarios.",
    backstory="""You are an expert in Behavior-Driven Development and proficient in generating Python scripts for the Behave library.
                 Your task is to convert each feature and its associated scenarios into a properly structured Behave feature file and corresponding Python step definitions.
                 You have extensive experience in Python and the Behave library, ensuring that the generated scripts are syntactically correct and follow best practices.
                 Your output should include both the feature file and the corresponding step definition scripts. Ensure coverage of all scenarios and include proper imports and comments.
                 NOTE:Provide a complete output.
                 """,
    allow_delegation=False,
    max_iter=100,
    verbose=True,
    llm=llm
)


# Creating the task for requirement generation which is done by the requirement_generator agent
requirements = Task(
    description=f"""Following these guidelines, generate system requirements using the provided Software Requirement Specifications(SRS) {full_pdf_content} in a clear and concise manner:

                    1. Identify each functionality and scenario described.
                    2. For each identified functionality, create a requirement with a unique identifier (e.g., REQ-001, REQ-002...).
                    3. Ensure requirements are phrased as clear and unambiguous statements using complete sentences.
                    6. Organize the requirements in an Excel file with columns: Requirement ID | Requirement Description

                    NOTE: Please generate the requirements based on the provided Software Requirement Specifications(SRS) only.
                    **IMPORTANT**: Ensure no requirement is left out. If necessary, continue generating additional files to include all requirements
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
    output_file = "requirements6.csv",
    agent=requirement_agent
)


# Creating Task for Feature Generation from Requirements
feature_generation_task = Task(
    description=f"""Analyze the provided system requirements  using the provided Software Requirement Specifications(SRS)  and generate a list of distinct features. Each feature should be clearly defined, unique, and relevant to the system being described.

                   """,
    expected_output="""Format your response as if you were describing the contents of an Excel file:
                        Feature ID | Feature Description | Requirement ID

                        FTE-001 | <feature1> | <requirement_id>
                        FTE-002 | <feature2> | <requirement_id>
                           .
                           .
                           .
                        IMPORTANT: Your response should be a valid Excel file (.xlsx).
                                  Your response must consist only of the table structure.
                                  Do not add any additional text, explanations, or summary lines before or after the table.
                                  The response should start with the header row and end with the last data row of the table.
                                  Ensure no feature is left out. If necessary, continue generating additional files to include all requirements
                        """,
    output_file="features6.csv",
    agent=feature_generation_agent,
    context=[requirements]
)

# Creating Task for Scenario Generation from Features
scenario_generation_task = Task(
    description=f"""For each feature identified in the previous task, generate all possible scenarios, including positive, negative, boundary, and edge cases  using the provided Software Requirement Specifications(SRS) .
                    """,
    expected_output="""Format your response as if you were describing the contents of an Excel file where each scenario is described clearly for each feature:
                        Feature ID | Scenario Number | Scenario Description

                        FTE-001 | SCENARIO-001 | <scenario description>
                        FTE-002 | SCENARIO-001 | <scenario description>
                           .
                           .
                           .
                    IMPORTANT: Your response should be a valid CSV file (.csv) with pipe (|) delimiter.
                               Your response must consist only of the table structure.
                               Do not add any additional text, explanations, or summary lines before or after the table.
                               The response should start with the header row and end with the last data row of the table.
                               Ensure comprehensive coverage of scenarios for each feature.Ensure no scenario is left out. If necessary, continue generating all scenarios
                    """,
    output_file="scenarios6.csv",
    agent=scenario_generation_agent,
    context=[feature_generation_task, requirements]
)

testcases = Task(
    description=f"""Based on the provided system requirements  using the provided Software Requirement Specifications(SRS) , generate comprehensive Gherkin test cases in a tabular format suitable for an Excel file with columns.
                    """,
    expected_output="""Format your response as if you were describing the contents of an Excel file:

                        Test Case ID | Feature | Scenario | Steps | Requirement ID

                        TEST-001     | <feature_name> | <scenario_name> | Given <precondition> When <action> And <action> But <action> Then <expected_result> And <expected_result>| <requirement_id>

                        TEST-002     | <feature_name> | <scenario_name> | Given <precondition> When <action> And <action> But <action> Then <expected_result> And <expected_result>| <requirement_id>

                            .
                            .
                            .
                    IMPORTANT: Your response should be a valid Excel file (.xlsx).
                               Your response must consist only of the table structure.
                               Do not add any additional text, explanations, or summary lines before or after the table.
                               The response should start with the header row and end with the last data row of the table.
                               Ensure all features and scenarios are covered.
                               Ensure no testcase is left out. If necessary, Continue generating all testcases
                    """,
    output_file="testcases6.csv",
    agent=testcase_agent,
    context=[feature_generation_task,scenario_generation_task, requirements]
)

# Review by QA agent
quality_assurance_task = Task(
    description=f"""You are a Quality Assurance expert tasked with reviewing the test cases generated in the previous step.
                  Identify any missing test cases, edge cases, or boundary conditions that have not been covered by the previous set of test cases  using the provided Software Requirement Specifications(SRS) .
                  Review the test cases and generate the necessary additions, if any.
                  """,
    expected_output="""Provide a table with the missing test cases identified, if any.
                      The table should contain:

                      Test Case ID | Feature | Scenario | Steps | Requirement ID

                      TEST-004     | <feature_name> | <scenario_name> | Given <precondition> When <action> And <action> But <action> Then <expected_result> And <expected_result>| <requirement_id>

                      TEST-009     | <feature_name> | <scenario_name> | Given <precondition> When <action> And <action> But <action> Then <expected_result> And <expected_result>| <requirement_id>

                          .
                          .
                          .
                      """,
    output_file="missing_test_cases6.csv",
    agent=quality_assurance_agent,
    context=[testcases,requirements]
)


# Creating a task to use the Behave Script Generator agent
behave_script_task = Task(
    description="""Convert the provided features and scenarios into Behave feature files and Python step definitions.
                  Generate the following output for each feature:

                  1. A feature file (.feature) containing all scenarios for the feature.
                  2. A Python step definition file (.py) implementing the steps for the scenarios.

                  Ensure the generated files adhere to the following structure:

                  **Feature File Format (.feature):**
                  Feature: <Feature Description>

                    Scenario: <Scenario Description>
                        Given <precondition>
                        When <action>
                        And <action>
                        But <action
                        Then <expected result>
                        And <expected result>

                  **Step Definition File Format (.py):**
                  # Imports
                  from behave import given, when, then

                  # Step Definitions
                  @given('<precondition>')
                  def step_given(context):
                      pass

                  @when('<action>')
                  def step_when(context):
                      pass

                  @then('<expected result>')
                  def step_then(context):
                      pass

                **How Gherkin is converted to Behave:**

                The conversion process involves the following steps:

                1. **Feature Files:** The Gherkin feature file (`.feature`) remains largely unchanged. It serves as the blueprint for the tests.
                2. **Step Definitions:** Each step in the feature file (Given, When, Then) is mapped to a Python function in the step definition file (`.py`).
                3. **Decorators:** Behave uses decorators (`@given`, `@when`, `@then`) to link the Gherkin steps to their corresponding Python functions.
                4. **Context:** The `context` object is passed to each step function. It's used to share data between steps and store the state of the test.
                5. **Assertions:** Assertions are used in the step definition functions to verify the expected outcomes of the test.

                ```
                **Example Input Feature:**
                        Feature: User Login

                          Scenario: Successful Login with Valid Credentials
                              Given the user is on the login page
                              When the user enters valid credentials
                              Then the user is redirected to the dashboard

                   ** Example Output Files:**

                    **user_login.feature**
                    Feature: User Login

                      Scenario: Successful Login with Valid Credentials
                          Given the user is on the login page
                          When the user enters valid credentials
                          Then the user is redirected to the dashboard

                    **user_login.py**
                    from behave import given, when, then

                    @given("the user is on the login page")
                    def step_impl(context):
                        context.page = "login page"

                    @when("the user enters valid credentials")
                    def step_impl(context):
                        context.credentials = "valid"

                    @then("the user is redirected to the dashboard")
                    def step_impl(context):
                        assert context.credentials == "valid"
                        context.page = "dashboard"
                        assert context.page == "dashboard"
                ```

                    Explanation:
                    - **Feature File:**
                        - Written in Gherkin syntax.
                        - Defines the feature, scenario, and steps (Given, When, Then).
                    - **Step Definition File:**
                        - Implements the logic for each step using Python functions.
                        - Decorators (`@given`, `@when`, `@then`) link the Gherkin steps to Python functions.
                        - The `context` object shares data between steps and validates outcomes using assertions.

                  **IMPORTANT:** Ensure comprehensive coverage of all scenarios and proper mapping between feature files and step definitions.
                                 Ensure no feature is left out. If necessary, continue generating additional files to include all feature files""",
    expected_output="""Provide a json format containing all the generated feature files and step definition scripts.
                      Each feature should have a corresponding feature file (.feature) and step definition file (.py).
                      The file should be well-organized into subfolders if there are multiple features.
                        **IMPORTANT**: Ensure no feature is left out. If necessary, continue generating additional files to include all features
                            {
                                "adaptive_cruise_control": (
                                    "Feature: Adaptive Cruise Control
                                        Scenario: Maintain speed in free road
                                            Given the vehicle is moving at 60 mph
                                            When there are no vehicles ahead
                                            Then the vehicle should maintain its speed
                                    ",
                                   "from behave import given, when, then

                                    @given('the vehicle is moving at {speed} mph')
                                    def given_vehicle_speed(context, speed):
                                        context.speed = int(speed)

                                    @when('there are no vehicles ahead')
                                    def when_no_vehicles_ahead(context):
                                        context.road_clear = True

                                    @then('the vehicle should maintain its speed')
                                    def then_maintain_speed(context):
                                        assert context.road_clear and context.speed == 60
                                    "
                                    ),
                                "lane_keeping_assist": (
                                    "Feature: Lane Keeping Assist
                                        Scenario: Keep the vehicle centered in lane
                                            Given the vehicle is moving within a lane
                                            When the vehicle drifts slightly
                                            Then the system should apply corrective steering
                                    ",
                                       "from behave import given, when, then

                                        @given('the vehicle is moving within a lane')
                                        def given_vehicle_in_lane(context):
                                            context.in_lane = True

                                        @when('the vehicle drifts slightly')
                                        def when_vehicle_drifts(context):
                                            context.drifts = True

                                        @then('the system should apply corrective steering')
                                        def then_correct_steering(context):
                                            assert context.in_lane and context.drifts
                                    "
                                )
                            }
                      """,
    output_file="behave_scripts6.json",
    agent=behave_script_agent,
    context=[testcases, quality_assurance_task]
)

# Make sure agents are instantiated properly and avoid any conflict with the configuration.
agents = [requirement_agent, feature_generation_agent, scenario_generation_agent, testcase_agent, quality_assurance_agent, behave_script_agent]

tasks = [requirements, feature_generation_task, scenario_generation_task, testcases, quality_assurance_task, behave_script_task]

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


csv_to_excel("requirements6.csv", "requirements6.xlsx","|")
csv_to_excel("features6.csv", "features6.xlsx", "|")
csv_to_excel("scenarios6.csv", "scenarios6.xlsx", "|")
csv_to_excel("testcases6.csv", "testcases6.xlsx","|")
csv_to_excel("missing_test_cases6.csv", "missing_test_cases6.xlsx","|")




import os
import json  # Assuming the input file is stored in a JSON format

class BehaveScriptSaver:
    def __init__(self, output_directory):
        """
        Initializes the script saver with a base output directory.
        :param output_directory: Base directory where feature files should be stored.
        """
        self.output_directory = output_directory

    def save_behave_scripts(self, feature_data):
        """
        Saves multiple Behave scripts into a structured folder format.

        :param feature_data: A dictionary where keys are feature names and values are tuples
                             containing (feature_content, step_definitions).
        """
        # Check if feature_data is None and handle it gracefully
        if feature_data is None:
            print("Error: feature_data is None. Check if the input file is valid or exists.")
            return  # Exit the function to avoid further errors

        for feature_name, (feature_content, step_definitions) in feature_data.items():
            # Define feature directory and steps subdirectory
            feature_dir = os.path.join(self.output_directory, feature_name)
            steps_dir = os.path.join(feature_dir, "steps")

            # Create directories if they don't exist
            os.makedirs(steps_dir, exist_ok=True)

            # Define file paths
            feature_file_path = os.path.join(feature_dir, f"{feature_name}.feature")
            step_file_path = os.path.join(steps_dir, f"{feature_name}.py")

            # Write feature file
            with open(feature_file_path, "w", encoding="utf-8") as f:
                f.write(feature_content)

            # Write step definition file
            with open(step_file_path, "w", encoding="utf-8") as f:
                f.write(step_definitions)

            print(f"Saved feature '{feature_name}' in {feature_dir}")

# Example usage
if __name__ == "__main__":
    output_directory = "output_directory6"  # Change this as needed
    # Read the file and parse the content

    # Read the file and parse the content
    # with open("/content/behave_scripts6.json", "r", encoding="utf-8") as file:
    #     try:
    #         # Assuming the file follows a JSON-like structure
    #         behave_script_data = json.load(file)
    #     except json.JSONDecodeError:
    #         print("Error: Invalid JSON format in behave_scripts6.json")
    #         exit(1)
    behave_script_data={
 "fte-001": (
  """Feature: APA Activation and Deactivation
    Scenario: Activate APA when the vehicle is in motion
      Given the vehicle is in motion
      When the Driver presses the APA button in the center console
      Then APA is activated
      And HMI displays a message indicating that APA is active

    Scenario: Do not activate APA when the vehicle is not in motion
      Given the vehicle is not in motion
      When the Driver presses the APA button in the center console
      Then APA is not activated
      And HMI displays a message indicating that APA is not active

    Scenario: Do not activate APA when the vehicle is in motion and the APA button is pressed multiple times
      Given the vehicle is in motion
      When the Driver presses the APA button in the center console multiple times
      Then APA is not activated
      And HMI displays a message indicating that APA cannot be activated while the vehicle is in motion

    Scenario: Activate APA when the vehicle is not in motion and the APA button is pressed
      Given the vehicle is not in motion
      When the Driver presses the APA button in the center console
      Then APA is activated
      And HMI displays a message indicating that APA is active

    Scenario: Do not deactivate APA when the APA button is not pressed
      Given the vehicle is in motion
      When APA is activated
      Then APA will not be deactivated
      And HMI does not display a message indicating that APA has been deactivated

    Scenario: Do not activate APA when the APA button is pressed multiple times and APA is not activated
      Given the vehicle is in motion
      When APA is not activated
      Then APA will not be activated
      And HMI does not display a message indicating that APA has been activated

    Scenario: Do not deactivate APA when the APA button is pressed and the vehicle is in motion
      Given the vehicle is in motion
      When APA is activated
      Then APA will not be deactivated
      And HMI does not display a message indicating that APA has been deactivated
   """,
  """from behave import *

    @given('the vehicle is in motion')
    def step_impl(context):
        context.vehicle_in_motion = True

    @given('the vehicle is not in motion')
    def step_impl(context):
        context.vehicle_in_motion = False

    @when('the Driver presses the APA button in the center console')
    def step_impl(context):
        context.apa_button_pressed = True

    @when('the Driver presses the APA button in the center console multiple times')
    def step_impl(context):
        context.apa_button_pressed_multiple_times = True

    @then('APA is activated')
    def step_impl(context):
        assert context.apa_button_pressed and context.vehicle_in_motion
        context.apa_activated = True

    @then('APA is not activated')
    def step_impl(context):
        assert not context.apa_button_pressed or not context.vehicle_in_motion
        context.apa_activated = False

    @then('HMI displays a message indicating that APA is active')
    def step_impl(context):
        assert context.apa_activated
        context.hmi_message_apa_active = True

    @then('HMI displays a message indicating that APA is not active')
    def step_impl(context):
        assert not context.apa_activated
        context.hmi_message_apa_not_active = True

    @then('APA will not be deactivated')
    def step_impl(context):
        assert not context.apa_button_pressed or context.vehicle_in_motion
        context.apa_deactivated = False

    @then('HMI does not display a message indicating that APA has been deactivated')
    def step_impl(context):
        assert not context.apa_deactivated
        context.hmi_message_apa_not_deactivated = True
    """
   ),
 "fte-002": (
  """Feature: HMI Display
    Scenario: Display HMI when the vehicle is in motion
      Given the vehicle is in motion
      When HMI is displayed on the 8-inch touch screen
      Then the Driver can view the HMI
      And the HMI displays information about the vehicle's surroundings

    Scenario: Do not display HMI when the vehicle is not in motion
      Given the vehicle is not in motion
      When HMI is not displayed on the 8-inch touch screen
      Then the Driver cannot view the HMI
      And the HMI does not display information about the vehicle's surroundings

    Scenario: Do not display HMI when the vehicle is in motion and HMI is not visible to the Driver
      Given the vehicle is in motion
      When HMI is displayed on the 8-inch touch screen but is not visible to the Driver
      Then the Driver cannot view the HMI
      And the HMI does not display information about the vehicle's surroundings

    Scenario: Do not interact with HMI when the vehicle is in motion and HMI is not responsive to touch
      Given the vehicle is in motion
      When HMI is displayed on the 8-inch touch screen but is not responsive to touch
      Then the Driver cannot interact with the HMI
      And the HMI does not respond to touch input

    Scenario: Display HMI when the vehicle is not in motion and HMI is displayed on the 8-inch touch screen
      Given the vehicle is not in motion
      When HMI is displayed on the 8-inch touch screen
      Then the Driver can view the HMI
      And the HMI displays information about the vehicle's surroundings

    Scenario: Do not display HMI when the vehicle is not in motion and HMI is not displayed on the 8-inch touch screen
      Given the vehicle is not in motion
      When HMI is not displayed on the 8-inch touch screen
      Then the Driver cannot view the HMI
      And the HMI does not display information about the vehicle's surroundings

    Scenario: Do not display HMI when the vehicle is not in motion and HMI is displayed on the 8-inch touch screen but is not visible to the Driver
      Given the vehicle is not in motion
      When HMI is displayed on the 8-inch touch screen but is not visible to the Driver
      Then the Driver cannot view the HMI
      And the HMI does not display information about the vehicle's surroundings

    Scenario: Do not interact with HMI when the vehicle is not in motion and HMI is displayed on the 8-inch touch screen but is not responsive to touch
      Given the vehicle is not in motion
      When HMI is displayed on the 8-inch touch screen but is not responsive to touch
      Then the Driver cannot interact with the HMI
      And the HMI does not respond to touch input
   """,
  """from behave import *

    @given('the vehicle is in motion')
    def step_impl(context):
        context.vehicle_in_motion = True

    @given('the vehicle is not in motion')
    def step_impl(context):
        context.vehicle_in_motion = False

    @when('HMI is displayed on the 8-inch touch screen')
    def step_impl(context):
        context.hmi_displayed = True

    @when('HMI is not displayed on the 8-inch touch screen')
    def step_impl(context):
        context.hmi_displayed = False

    @when('HMI is displayed on the 8-inch touch screen but is not visible to the Driver')
    def step_impl(context):
        context.hmi_visible = False

    @when('HMI is displayed on the 8-inch touch screen but is not responsive to touch')
    def step_impl(context):
        context.hmi_responsive = False

    @then('the Driver can view the HMI')
    def step_impl(context):
        assert context.hmi_displayed and context.hmi_visible
        context.driver_can_view_hmi = True

    @then('the Driver cannot view the HMI')
    def step_impl(context):
        assert not context.hmi_displayed or not context.hmi_visible
        context.driver_can_view_hmi = False

    @then('the HMI displays information about the vehicle's surroundings')
    def step_impl(context):
        assert context.hmi_displayed and context.vehicle_in_motion
        context.hmi_displays_vehicle_surroundings = True

    @then('the HMI does not display information about the vehicle's surroundings')
    def step_impl(context):
        assert not context.hmi_displayed or not context.vehicle_in_motion
        context.hmi_displays_vehicle_surroundings = False

    @then('the Driver cannot interact with the HMI')
    def step_impl(context):
        assert not context.hmi_responsive
        context.driver_can_interact_with_hmi = False

    @then('the HMI does not respond to touch input')
    def step_impl(context):
        assert not context.hmi_responsive
        context.hmi_responds_to_touch = False
    """
 )
    }

    # Initialize and execute saving process
    saver = BehaveScriptSaver(output_directory)
    saver.save_behave_scripts(behave_script_data) # behave_script_data is now accessible
