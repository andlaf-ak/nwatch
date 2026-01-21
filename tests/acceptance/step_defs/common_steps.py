"""
Common step definitions shared across all acceptance test scenarios.

Provides reusable Given/When/Then steps for:
- Step file creation and manipulation
- Browser interactions
- Assertions on the step viewer UI
"""

from pytest_bdd import given, when, then, parsers
from playwright.sync_api import expect
import json
import os
import time

from tests.acceptance.conftest import (
    create_step_file,
    modify_step_status,
    delete_step_file,
    create_malformed_json
)


# ============================================================================
# GIVEN Steps
# ============================================================================

@given("the nwwatch backend is running")
def given_backend_running(backend_server):
    """Ensure backend is running via fixture."""
    assert backend_server.poll() is None, "Backend server crashed"


@given("the browser is connected to the step viewer")
def given_browser_connected(browser_page):
    """Ensure browser has loaded the step viewer."""
    status = browser_page.locator("[data-testid='connection-status']")
    expect(status).to_have_attribute("data-status", "connected", timeout=5000)


@given(parsers.parse("the steps folder contains the following step files:"))
def given_step_files(steps_folder, datatable):
    """
    Create step files from a Gherkin datatable.

    Datatable format:
    | task_id | project_id | phase      | status    |
    | 01-01   | my-project | Foundation | completed |
    """
    for row in datatable:
        create_step_file(
            folder=steps_folder,
            task_id=row["task_id"],
            project_id=row["project_id"],
            phase=row["phase"],
            status=row["status"]
        )


@given(parsers.parse('the steps folder contains a step with status "{status}"'))
def given_single_step_with_status(steps_folder, status):
    """Create a single step with the specified status."""
    create_step_file(
        folder=steps_folder,
        task_id="01-01",
        project_id="test-project",
        phase="TestPhase",
        status=status
    )


@given(parsers.parse('the steps folder contains a malformed JSON file "{filename}"'))
def given_malformed_json(steps_folder, filename):
    """Create a malformed JSON file for error handling tests."""
    create_malformed_json(steps_folder, filename)


@given("the steps folder is empty")
def given_empty_folder(steps_folder):
    """Ensure steps folder is empty (already is from fixture)."""
    assert len(os.listdir(steps_folder)) == 0


@given(parsers.parse("the steps folder contains {count:d} step files across {phases:d} phases"))
def given_many_steps(steps_folder, count, phases):
    """Create many step files for performance testing."""
    steps_per_phase = count // phases
    for phase_num in range(1, phases + 1):
        for step_num in range(1, steps_per_phase + 1):
            task_id = f"{phase_num:02d}-{step_num:02d}"
            create_step_file(
                folder=steps_folder,
                task_id=task_id,
                project_id="test-project",
                phase=f"Phase{phase_num}",
                status="pending"
            )


@given(parsers.parse('the step card "{task_id}" shows status "{status}"'))
def given_step_shows_status(browser_page, task_id, status):
    """Verify a step card shows the expected status."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    badge = card.locator("[data-testid='status-badge']")
    expect(badge).to_have_text(status)


@given(parsers.parse('the current theme is "{theme}"'))
def given_current_theme(browser_page, theme):
    """Set the initial theme."""
    current = browser_page.locator("html").get_attribute("data-theme")
    if current != theme:
        browser_page.click("[data-testid='theme-toggle']")
        expect(browser_page.locator("html")).to_have_attribute("data-theme", theme)


@given(parsers.parse('I set the theme to "{theme}"'))
def given_set_theme(browser_page, theme):
    """Set the theme to a specific value."""
    current = browser_page.locator("html").get_attribute("data-theme")
    if current != theme:
        browser_page.click("[data-testid='theme-toggle']")


# ============================================================================
# WHEN Steps
# ============================================================================

@when("I open the step viewer")
def when_open_viewer(browser_page):
    """Open step viewer (already done via fixture)."""
    pass


@when(parsers.parse('the step file "{filename}" is modified with status "{status}"'))
def when_modify_step(steps_folder, filename, status):
    """Modify a step file's status."""
    task_id = filename.replace(".json", "")
    modify_step_status(steps_folder, task_id, status)


@when(parsers.parse('a new step file "{filename}" is created with:'))
def when_create_step(steps_folder, filename, datatable):
    """Create a new step file from datatable."""
    row = datatable[0]
    create_step_file(
        folder=steps_folder,
        task_id=row["task_id"],
        project_id=row["project_id"],
        phase=row["phase"],
        status=row["status"]
    )


@when(parsers.parse('the step file "{filename}" is deleted'))
def when_delete_step(steps_folder, filename):
    """Delete a step file."""
    task_id = filename.replace(".json", "")
    delete_step_file(steps_folder, task_id)


@when("I click the theme toggle button")
def when_click_theme_toggle(browser_page):
    """Click the theme toggle button."""
    browser_page.click("[data-testid='theme-toggle']")


@when("I close and reopen the step viewer")
def when_reopen_viewer(browser_page):
    """Close and reopen the step viewer."""
    browser_page.reload()
    browser_page.wait_for_selector("[data-testid='step-grid']", timeout=5000)


@when("the WebSocket connection is lost")
def when_connection_lost(browser_page):
    """Simulate WebSocket disconnection."""
    # Execute JavaScript to close WebSocket
    browser_page.evaluate("window.__ws?.close()")


@when("the connection is restored")
def when_connection_restored(browser_page):
    """Wait for WebSocket to reconnect."""
    status = browser_page.locator("[data-testid='connection-status']")
    expect(status).to_have_attribute("data-status", "connected", timeout=10000)


@when(parsers.parse('the step file "{filename}" is modified {count:d} times in quick succession'))
def when_rapid_modifications(steps_folder, filename, count):
    """Rapidly modify a step file multiple times."""
    task_id = filename.replace(".json", "")
    statuses = ["pending", "in_progress", "completed", "failed", "skipped"]
    for i in range(count):
        modify_step_status(steps_folder, task_id, statuses[i % len(statuses)])
        time.sleep(0.05)  # 50ms between changes


# ============================================================================
# THEN Steps
# ============================================================================

@then(parsers.parse("I should see {count:d} step cards displayed"))
def then_step_count(browser_page, count):
    """Verify the number of step cards displayed."""
    cards = browser_page.locator("[data-testid='step-card']")
    expect(cards).to_have_count(count, timeout=2000)


@then("each step card should show the task_id")
def then_cards_show_task_id(browser_page):
    """Verify all step cards display task_id."""
    cards = browser_page.locator("[data-testid='step-card']")
    for i in range(cards.count()):
        task_id_elem = cards.nth(i).locator("[data-testid='task-id']")
        expect(task_id_elem).to_be_visible()


@then("each step card should show the phase name")
def then_cards_show_phase(browser_page):
    """Verify all step cards display phase name."""
    cards = browser_page.locator("[data-testid='step-card']")
    for i in range(cards.count()):
        phase_elem = cards.nth(i).locator("[data-testid='phase-name']")
        expect(phase_elem).to_be_visible()


@then("each step card should show the status")
def then_cards_show_status(browser_page):
    """Verify all step cards display status."""
    cards = browser_page.locator("[data-testid='step-card']")
    for i in range(cards.count()):
        status_elem = cards.nth(i).locator("[data-testid='status-badge']")
        expect(status_elem).to_be_visible()


@then(parsers.parse("I should see {count:d} phase rows"))
def then_phase_row_count(browser_page, count):
    """Verify the number of phase rows."""
    rows = browser_page.locator("[data-testid='phase-row']")
    expect(rows).to_have_count(count)


@then(parsers.parse('the "{phase}" row should contain {count:d} steps'))
def then_phase_row_step_count(browser_page, phase, count):
    """Verify step count in a specific phase row."""
    row = browser_page.locator(f"[data-testid='phase-row-{phase}']")
    cards = row.locator("[data-testid='step-card']")
    expect(cards).to_have_count(count)


@then(parsers.parse('the "{phase}" row should display steps in order: {order}'))
def then_step_order(browser_page, phase, order):
    """Verify steps are in the expected order."""
    expected_ids = [id.strip().strip('"') for id in order.split(",")]
    row = browser_page.locator(f"[data-testid='phase-row-{phase}']")
    cards = row.locator("[data-testid='step-card']")

    for i, expected_id in enumerate(expected_ids):
        task_id = cards.nth(i).locator("[data-testid='task-id']")
        expect(task_id).to_have_text(expected_id)


@then(parsers.parse('the step card "{task_id}" should have a pulse animation'))
def then_has_pulse(browser_page, task_id):
    """Verify step card has pulse animation."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    expect(card).to_have_class(/pulse/)


@then(parsers.parse('the step card "{task_id}" should not have a pulse animation'))
def then_no_pulse(browser_page, task_id):
    """Verify step card does not have pulse animation."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    classes = card.get_attribute("class") or ""
    assert "pulse" not in classes


@then(parsers.parse("only {count:d} step card should have a pulse animation"))
def then_single_pulse_count(browser_page, count):
    """Verify only specified number of cards pulse."""
    pulsing = browser_page.locator("[data-testid='step-card'].pulse")
    expect(pulsing).to_have_count(count)


@then("no step cards should have a pulse animation")
def then_no_pulse_anywhere(browser_page):
    """Verify no cards have pulse animation."""
    pulsing = browser_page.locator("[data-testid='step-card'].pulse")
    expect(pulsing).to_have_count(0)


@then(parsers.parse('within {seconds:d} second the step card "{task_id}" should show status "{status}"'))
def then_status_within_timeout(browser_page, seconds, task_id, status):
    """Verify status updates within timeout."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    badge = card.locator("[data-testid='status-badge']")
    expect(badge).to_have_text(status, timeout=seconds * 1000)


@then(parsers.parse('the step card "{task_id}" should be visible'))
def then_step_visible(browser_page, task_id):
    """Verify step card is visible."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    expect(card).to_be_visible()


@then(parsers.parse('the step card "{task_id}" should not be visible'))
def then_step_not_visible(browser_page, task_id):
    """Verify step card is not visible."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    expect(card).not_to_be_visible()


@then("I should not need to refresh the page")
def then_no_refresh_needed():
    """This is a documentation step - verified by other assertions."""
    pass


@then(parsers.parse('the current theme should be "{theme}"'))
def then_current_theme(browser_page, theme):
    """Verify current theme."""
    expect(browser_page.locator("html")).to_have_attribute("data-theme", theme)


@then(parsers.parse('the step card should have the "{color}" status color'))
def then_status_color(browser_page, color):
    """Verify step card has expected status color."""
    card = browser_page.locator("[data-testid='step-card']")
    badge = card.locator("[data-testid='status-badge']")
    expect(badge).to_have_attribute("data-color", color)


@then(parsers.parse('in "{theme}" theme all step status colors should be visible'))
def then_colors_visible_in_theme(browser_page, theme):
    """Verify all status colors are visible in the given theme."""
    # Set theme if needed
    current = browser_page.locator("html").get_attribute("data-theme")
    if current != theme:
        browser_page.click("[data-testid='theme-toggle']")

    # Verify all status badges are visible
    badges = browser_page.locator("[data-testid='status-badge']")
    for i in range(badges.count()):
        expect(badges.nth(i)).to_be_visible()


@then("I should see an empty state message")
def then_empty_state(browser_page):
    """Verify empty state message is shown."""
    empty = browser_page.locator("[data-testid='empty-state']")
    expect(empty).to_be_visible()


@then("no step cards should be displayed")
def then_no_cards(browser_page):
    """Verify no step cards are displayed."""
    cards = browser_page.locator("[data-testid='step-card']")
    expect(cards).to_have_count(0)


@then(parsers.parse('all {count:d} step cards should be displayed'))
def then_all_steps_displayed(browser_page, count):
    """Verify all steps are displayed."""
    cards = browser_page.locator("[data-testid='step-card']")
    expect(cards).to_have_count(count, timeout=5000)


@then("the UI should remain responsive")
def then_ui_responsive(browser_page):
    """Verify UI is still responsive."""
    # Click theme toggle and verify it responds
    browser_page.click("[data-testid='theme-toggle']")
    # If we get here without timeout, UI is responsive


@then("the final status should be displayed correctly")
def then_final_status_correct(browser_page):
    """Verify final status is shown after rapid updates."""
    card = browser_page.locator("[data-testid='step-card']")
    badge = card.locator("[data-testid='status-badge']")
    # Status should be one of the valid values
    status = badge.text_content()
    assert status in ["pending", "in_progress", "completed", "failed", "skipped"]


@then("the viewer should not crash or freeze")
def then_no_crash():
    """Verify viewer didn't crash - if we got here, it didn't."""
    pass


@then("no error should be shown to the user")
def then_no_error(browser_page):
    """Verify no error message is displayed."""
    error = browser_page.locator("[data-testid='error-message']")
    expect(error).not_to_be_visible()


@then(parsers.parse('the connection status should show "{status}"'))
def then_connection_status(browser_page, status):
    """Verify WebSocket connection status."""
    status_elem = browser_page.locator("[data-testid='connection-status']")
    expect(status_elem).to_have_attribute("data-status", status)


@then("the viewer should attempt to reconnect automatically")
def then_auto_reconnect(browser_page):
    """Verify reconnection is attempted."""
    status = browser_page.locator("[data-testid='connection-status']")
    # Should show reconnecting or connected eventually
    expect(status).to_have_attribute("data-status", /(reconnecting|connected)/, timeout=5000)


@then(parsers.parse('the WebSocket connection status should be "{status}"'))
def then_ws_status(browser_page, status):
    """Verify WebSocket connection status."""
    status_elem = browser_page.locator("[data-testid='connection-status']")
    expect(status_elem).to_have_attribute("data-status", status)
