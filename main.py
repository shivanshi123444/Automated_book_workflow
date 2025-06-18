# src/main.py
import asyncio
import os
import uuid
from scraper import fetch_content_and_screenshot
from ai_processor import ai_spin_chapter, ai_review_chapter # This will now be the SIMULATED version
from version_manager import save_chapter_version, retrieve_consistent_content_rl_search, get_chapter_versions
from human_interface import get_human_feedback, get_human_decision, apply_human_edits
from config import RAW_CONTENT_DIR, PROCESSED_CHAPTERS_DIR, SCREENSHOTS_DIR # Imported for context, not directly used here

async def workflow_chapter_processing(
    chapter_url: str,
    chapter_name: str,
    max_ai_iterations: int = 3, # Maximum times AI will attempt to spin/review a chapter
    max_human_sub_iterations: int = 2 # Maximum times human can provide feedback/edit within one AI iteration
):
    """
    Orchestrates the entire automated book publication workflow for a single chapter.
    This includes scraping, AI processing (simulated), human review, and version management.
    """
    print(f"\n--- Starting Workflow for Chapter: {chapter_name} ---")

    # Create a unique, URL-safe ID for the chapter for ChromaDB storage
    chapter_id = chapter_name.replace(" ", "_").lower().replace("/", "_").replace(":", "")

    # --- 1. Scraping & Screenshots ---
    print("\n[STEP 1/5] Scraping content and taking screenshot...")
    raw_content = await fetch_content_and_screenshot(chapter_url, chapter_name)
    if not raw_content:
        print(f"Failed to scrape content from {chapter_url}. Aborting workflow for this chapter.")
        return

    # Save the initial raw version to ChromaDB
    initial_version_id = str(uuid.uuid4())
    await save_chapter_version(chapter_id, initial_version_id, raw_content, "raw", 0)
    current_content = raw_content # The content being worked on
    previous_content_for_review = raw_content # What the AI reviewer will compare against

    iteration = 0
    workflow_status = "ongoing" # Controls the main loop (AI iterations)

    while workflow_status == "ongoing" and iteration < max_ai_iterations:
        iteration += 1
        print(f"\n--- Starting ITERATION {iteration} ---")

        # --- 2. AI Writing (Spin) ---
        print(f"\n[STEP 2/5] AI Writer is spinning chapter (Iteration {iteration})...")
        spun_content = await ai_spin_chapter(current_content, iteration)
        spun_version_id = str(uuid.uuid4())
        await save_chapter_version(chapter_id, spun_version_id, spun_content, "spun", iteration)
        current_content = spun_content # The AI's spun output becomes the new current content

        # --- 3. AI Review ---
        print(f"\n[STEP 3/5] AI Reviewer is analyzing spun chapter (Iteration {iteration})...")
        review_result = await ai_review_chapter(previous_content_for_review, spun_content, iteration)
        reviewed_version_id = str(uuid.uuid4())
        # Store review results as metadata; useful for the conceptual "RL Search"
        await save_chapter_version(chapter_id, reviewed_version_id, spun_content, "reviewed", iteration, metadata=review_result)
        print(f"AI Review Feedback: {review_result.get('feedback', 'No feedback provided.')}")
        print(f"AI Review Suggestions: {review_result.get('suggestions', 'No suggestions provided.')}")

        # --- 4. Human-in-the-Loop ---
        print(f"\n[STEP 4/5] Human-in-the-Loop phase (Iteration {iteration})...")
        human_sub_iterations_count = 0
        human_decision = "" # Stores the human's choice for the current iteration

        # Loop for human feedback/edits within the current AI iteration
        while human_sub_iterations_count < max_human_sub_iterations and human_decision not in ["approve", "finalize", "stop", "re_spin_by_ai"]:
            human_feedback = get_human_feedback(chapter_name, current_content, f"Iteration {iteration} - Human Review ({human_sub_iterations_count + 1})")

            # Check for direct human commands
            if human_feedback.lower() == 'approve':
                human_decision = "approve"
                print("Human approved the current version.")
                break # Exit inner human loop
            elif human_feedback.lower() == 'finalize':
                human_decision = "finalize"
                print("Human finalized the current version. Marking as final.")
                break # Exit inner human loop
            elif human_feedback.lower() == 'stop':
                human_decision = "stop"
                workflow_status = "stopped" # Signals to exit main workflow loop
                print("Human requested to stop the workflow.")
                break # Exit inner human loop
            else:
                # Human provided specific feedback; prompt for action
                decision_options = [
                    "Edit content directly",
                    "Send back to AI for re-spin (based on this feedback)",
                    "Approve and proceed to next AI iteration",
                    "Finalize and publish this version",
                    "Stop workflow entirely"
                ]
                action_choice = get_human_decision("What action would you like to take?", decision_options)

                if action_choice == "Edit content directly":
                    current_content = apply_human_edits(current_content)
                    edited_version_id = str(uuid.uuid4())
                    # Save human edits as a distinct version
                    await save_chapter_version(chapter_id, edited_version_id, current_content, "human_edited", iteration)
                    print("Human edits applied. Please review the edited content.")
                    # After editing, loop back to allow human to review edited content or make another decision
                    continue # Continue inner human loop to prompt for feedback again

                elif action_choice == "Send back to AI for re-spin (based on this feedback)":
                    # This decision signals to restart the AI spin for the *current* iteration
                    # We can prepend the human feedback to the content for the AI to "consider"
                    current_content = f"HUMAN FEEDBACK TO CONSIDER FOR RE-SPIN: '{human_feedback}'\n\nOriginal content to re-spin:\n{previous_content_for_review}"
                    human_decision = "re_spin_by_ai"
                    print("Preparing to send feedback back to AI for the next spin.")
                    break # Break out of inner human loop to let main loop handle re-spinning

                elif action_choice == "Approve and proceed to next AI iteration":
                    human_decision = "approve"
                    print("Human approved the current version. Proceeding to next AI iteration.")
                    break # Exit inner human loop

                elif action_choice == "Finalize and publish this version":
                    human_decision = "finalize"
                    print("Human finalized the current version. Marking as final.")
                    break # Exit inner human loop

                elif action_choice == "Stop workflow entirely":
                    human_decision = "stop"
                    workflow_status = "stopped"
                    print("Human requested to stop the workflow.")
                    break # Exit inner human loop
            
            human_sub_iterations_count += 1
            if human_sub_iterations_count >= max_human_sub_iterations and human_decision not in ["approve", "finalize", "stop", "re_spin_by_ai"]:
                print(f"Max human sub-iterations reached ({max_human_sub_iterations}) for this AI iteration. Auto-proceeding to next AI iteration or finalizing if no more AI iterations.")
                human_decision = "auto_proceed" # Indicates no explicit human action, just move on

        # Handle decisions made in the human-in-the-loop phase
        if human_decision == "finalize":
            final_version_id = str(uuid.uuid4())
            await save_chapter_version(chapter_id, final_version_id, current_content, "final", iteration)
            print(f"Chapter '{chapter_name}' finalized and saved as final version.")
            workflow_status = "finalized" # Signal to exit main loop
            break # Exit main workflow loop

        if workflow_status == "stopped":
            print(f"Workflow stopped by human for chapter '{chapter_name}'.")
            break # Exit main workflow loop

        if human_decision == "re_spin_by_ai":
            # This 'continue' will make the outer 'while workflow_status == "ongoing"' loop
            # effectively re-run the current AI iteration (spinning with new 'current_content').
            print("Re-spinning with AI based on human feedback...")
            continue # Skip updating previous_content_for_review and go to next outer loop iteration

        # If human approved or auto_proceeded, prepare for the next full AI iteration
        # The content that was just approved/processed becomes the new "original" for the next AI review
        previous_content_for_review = current_content 

    # --- Workflow Completion / Finalization ---
    if workflow_status == "ongoing":
        print(f"\nMax AI iterations ({max_ai_iterations}) reached for chapter {chapter_name}. Workflow ending without explicit finalization.")
        # If workflow completed all AI iterations without explicit human finalization, save the last state
        last_version_id = str(uuid.uuid4())
        await save_chapter_version(chapter_id, last_version_id, current_content, "auto_finished", iteration)
        print("Last version saved as 'auto_finished'. Consider reviewing it manually for finalization.")

    # --- 5. Versioning & Consistency (Post-Workflow Retrieval Example) ---
    print(f"\n[STEP 5/5] Attempting to retrieve consistent content for '{chapter_name}' using RL search (conceptual)...")
    final_retrieved_content = await retrieve_consistent_content_rl_search(chapter_id)
    if final_retrieved_content:
        print(f"\n--- Retrieved Final/Best Version for '{chapter_name}' ---")
        print(f"Version ID: {final_retrieved_content['id']}")
        print(f"Version Type: {final_retrieved_content['metadata'].get('version_type', 'N/A')}")
        print(f"Iteration: {final_retrieved_content['metadata'].get('iteration', 'N/A')}")
        print(f"Content Sample:\n{final_retrieved_content['content'][:500]}...") # Display first 500 characters
    else:
        print(f"Could not retrieve a consistent final version for '{chapter_name}'.")

    print(f"\n--- Workflow for Chapter: {chapter_name} Completed ---")

async def main():
    # Define the chapter URL and a recognizable name for it
    chapter_to_process_url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
    chapter_to_process_name = "The Gates of Morning - Book 1 Chapter 1"

    await workflow_chapter_processing(chapter_to_process_url, chapter_to_process_name)

if __name__ == "__main__":
    asyncio.run(main())
