Feature: Simple Calculator

  Scenario: Add two numbers
    Given I have entered 50 into the calculator
    When I press add
    And I have entered 70 into the calculator
    Then the result should be 120 on the screen

  Scenario: Subtract two numbers
    Given I have entered 100 into the calculator
    When I press subtract
    And I have entered 30 into the calculator
    Then the result should be 70 on the screen

  Scenario: Multiply two numbers
    Given I have entered 10 into the calculator
    When I press multiply
    And I have entered 5 into the calculator
    Then the result should be 50 on the screen

  Scenario: Divide two numbers
    Given I have entered 100 into the calculator
    When I press divide
    And I have entered 10 into the calculator
    Then the result should be 10 on the screen

  Scenario: Divide by Zero
    Given I have entered 100 into the calculator
    When I press divide
    And I have entered 0 into the calculator
    Then I should see an error message "Division by zero"
