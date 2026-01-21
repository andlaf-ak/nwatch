# language: en
@nwwatch @step-viewer
Feature: nWave Step Viewer
  As a developer using the nWave framework
  I want to visualize my development steps in real-time
  So that I can track progress through the development phases

  Background:
    Given the nwwatch backend is running
    And the browser is connected to the step viewer

  # ===========================================================================
  # US-01: View All Steps
  # ===========================================================================

  @US-01 @initial-load
  Scenario: Display all steps from a steps folder
    Given the steps folder contains the following step files:
      | task_id | project_id | phase       | status    |
      | 01-01   | my-project | Foundation  | completed |
      | 01-02   | my-project | Foundation  | completed |
      | 02-01   | my-project | Entities    | pending   |
      | 02-02   | my-project | Entities    | pending   |
    When I open the step viewer
    Then I should see 4 step cards displayed
    And each step card should show the task_id
    And each step card should show the phase name
    And each step card should show the status

  @US-01 @phase-grouping
  Scenario: Steps are grouped by phase in rows
    Given the steps folder contains the following step files:
      | task_id | project_id | phase       | status    |
      | 01-01   | my-project | Foundation  | completed |
      | 01-02   | my-project | Foundation  | completed |
      | 02-01   | my-project | Entities    | pending   |
      | 02-02   | my-project | Entities    | pending   |
      | 03-01   | my-project | Managers    | pending   |
    When I open the step viewer
    Then I should see 3 phase rows
    And the "Foundation" row should contain 2 steps
    And the "Entities" row should contain 2 steps
    And the "Managers" row should contain 1 step

  @US-01 @step-ordering
  Scenario: Steps within a phase are ordered by minor version
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status    |
      | 01-03   | my-project | Foundation | pending   |
      | 01-01   | my-project | Foundation | completed |
      | 01-02   | my-project | Foundation | completed |
    When I open the step viewer
    Then the "Foundation" row should display steps in order: "01-01", "01-02", "01-03"

  # ===========================================================================
  # US-02: See Current Step (Pulsing)
  # ===========================================================================

  @US-02 @pulse-animation
  Scenario: The current in-progress step pulses
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status      |
      | 01-01   | my-project | Foundation | completed   |
      | 01-02   | my-project | Foundation | in_progress |
      | 01-03   | my-project | Foundation | pending     |
    When I open the step viewer
    Then the step card "01-02" should have a pulse animation
    And the step card "01-01" should not have a pulse animation
    And the step card "01-03" should not have a pulse animation

  @US-02 @single-pulse
  Scenario: Only the first in-progress step pulses when multiple exist
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status      |
      | 01-01   | my-project | Foundation | in_progress |
      | 01-02   | my-project | Foundation | in_progress |
      | 01-03   | my-project | Foundation | pending     |
    When I open the step viewer
    Then only 1 step card should have a pulse animation
    And the step card "01-01" should have a pulse animation

  @US-02 @no-pulse-when-no-in-progress
  Scenario: No steps pulse when none are in progress
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status    |
      | 01-01   | my-project | Foundation | completed |
      | 01-02   | my-project | Foundation | pending   |
    When I open the step viewer
    Then no step cards should have a pulse animation

  # ===========================================================================
  # US-03: Real-time Updates
  # ===========================================================================

  @US-03 @file-modification
  Scenario: Step status updates when file is modified
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status  |
      | 01-01   | my-project | Foundation | pending |
    And I open the step viewer
    And the step card "01-01" shows status "pending"
    When the step file "01-01.json" is modified with status "in_progress"
    Then within 1 second the step card "01-01" should show status "in_progress"
    And the step card "01-01" should have a pulse animation

  @US-03 @file-creation
  Scenario: New step appears when file is created
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status    |
      | 01-01   | my-project | Foundation | completed |
    And I open the step viewer
    And I should see 1 step card displayed
    When a new step file "01-02.json" is created with:
      | task_id | project_id | phase      | status  |
      | 01-02   | my-project | Foundation | pending |
    Then within 1 second I should see 2 step cards displayed
    And the step card "01-02" should be visible

  @US-03 @file-deletion
  Scenario: Step disappears when file is deleted
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status    |
      | 01-01   | my-project | Foundation | completed |
      | 01-02   | my-project | Foundation | pending   |
    And I open the step viewer
    And I should see 2 step cards displayed
    When the step file "01-02.json" is deleted
    Then within 1 second I should see 1 step card displayed
    And the step card "01-02" should not be visible

  @US-03 @no-refresh-required
  Scenario: Updates appear without page refresh
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status  |
      | 01-01   | my-project | Foundation | pending |
    And I open the step viewer
    When the step file "01-01.json" is modified with status "completed"
    Then I should not need to refresh the page
    And the step card "01-01" should show status "completed"

  # ===========================================================================
  # US-04: Toggle Theme
  # ===========================================================================

  @US-04 @theme-toggle
  Scenario: User can toggle between dark and light themes
    Given I open the step viewer
    And the current theme is "dark"
    When I click the theme toggle button
    Then the current theme should be "light"
    When I click the theme toggle button
    Then the current theme should be "dark"

  @US-04 @theme-persistence
  Scenario: Theme preference persists across browser sessions
    Given I open the step viewer
    And I set the theme to "light"
    When I close and reopen the step viewer
    Then the current theme should be "light"

  @US-04 @theme-contrast
  Scenario: Step colors have good contrast in both themes
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status      |
      | 01-01   | my-project | Foundation | pending     |
      | 01-02   | my-project | Foundation | in_progress |
      | 01-03   | my-project | Foundation | completed   |
      | 01-04   | my-project | Foundation | failed      |
      | 02-01   | my-project | Entities   | skipped     |
    And I open the step viewer
    Then in "dark" theme all step status colors should be visible
    And in "light" theme all step status colors should be visible

  # ===========================================================================
  # US-05: Start Viewer
  # ===========================================================================

  @US-05 @server-startup
  Scenario: Server starts with command line argument
    Given a steps folder exists at "/tmp/test-steps"
    When I run "python main.py /tmp/test-steps"
    Then the server should start successfully
    And the server should be watching the folder "/tmp/test-steps"
    And a browser can connect to "http://localhost:8000"

  @US-05 @websocket-connection
  Scenario: Browser establishes WebSocket connection
    Given the nwwatch backend is running
    When I open the step viewer in the browser
    Then the WebSocket connection status should be "connected"

  # ===========================================================================
  # Step Status Colors (Traffic Light)
  # ===========================================================================

  @status-colors
  Scenario Outline: Step cards display correct colors for each status
    Given the steps folder contains a step with status "<status>"
    When I open the step viewer
    Then the step card should have the "<color>" status color

    Examples:
      | status      | color  |
      | pending     | gray   |
      | in_progress | yellow |
      | completed   | green  |
      | failed      | red    |
      | skipped     | blue   |

  # ===========================================================================
  # Error Handling & Reliability
  # ===========================================================================

  @reliability @malformed-json
  Scenario: Malformed JSON files are handled gracefully
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status    |
      | 01-01   | my-project | Foundation | completed |
    And the steps folder contains a malformed JSON file "bad-file.json"
    When I open the step viewer
    Then I should see 1 step card displayed
    And no error should be shown to the user

  @reliability @websocket-reconnect
  Scenario: WebSocket reconnects after disconnection
    Given I open the step viewer
    And the WebSocket connection status is "connected"
    When the WebSocket connection is lost
    Then the connection status should show "disconnected"
    And the viewer should attempt to reconnect automatically
    When the connection is restored
    Then the WebSocket connection status should be "connected"

  @reliability @empty-folder
  Scenario: Empty steps folder shows empty state
    Given the steps folder is empty
    When I open the step viewer
    Then I should see an empty state message
    And no step cards should be displayed

  # ===========================================================================
  # Performance
  # ===========================================================================

  @performance @many-steps
  Scenario: Viewer handles 100 steps without degradation
    Given the steps folder contains 100 step files across 10 phases
    When I open the step viewer
    Then all 100 step cards should be displayed
    And the UI should remain responsive

  @performance @rapid-updates
  Scenario: Viewer handles rapid file changes
    Given the steps folder contains the following step files:
      | task_id | project_id | phase      | status  |
      | 01-01   | my-project | Foundation | pending |
    And I open the step viewer
    When the step file "01-01.json" is modified 10 times in quick succession
    Then the final status should be displayed correctly
    And the viewer should not crash or freeze
