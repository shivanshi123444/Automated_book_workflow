# src/human_interface.py
from typing import Dict, Any

def get_human_feedback(chapter_name: str, current_content: str, phase: str) -> str:
    """
    Prompts the human for feedback on the chapter content at a specific phase.
    """
    print(f"\n--- Human-in-the-Loop: {phase} for {chapter_name} ---")
    print(f"Current Content Preview (first 500 characters):\n{current_content[:500]}...")
    print("\nPlease review the content above carefully.")
    feedback = input("Enter your feedback/edits (or type 'approve' to proceed, 'finalize' to publish, 'stop' to halt workflow): ")
    return feedback

def get_human_decision(prompt_message: str, options: list) -> str:
    """
    Asks the human to make a decision from a list of numbered options.
    """
    print(f"\n{prompt_message}")
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    while True:
        choice = input(f"Enter your choice (1-{len(options)}): ")
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            else:
                print("Invalid choice. Please enter a number within the given range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def apply_human_edits(original_content: str) -> str:
    """
    Allows the human to directly edit the content in the terminal.
    Instructions are provided for multi-line input.
    """
    print("\n--- Human Editor: Apply Edits ---")
    print("Current content (you can copy, edit, and paste the modified version below):")
    print("--------------------------------------------------------------------")
    print(original_content)
    print("--------------------------------------------------------------------")
    print("Paste your edited content below. When finished, press Enter, then Ctrl+D (Unix/macOS) or Ctrl+Z then Enter (Windows).")

    edited_content_lines = []
    try:
        while True:
            line = input()
            edited_content_lines.append(line)
    except EOFError: # Raised when Ctrl+D or Ctrl+Z is pressed (end of file)
        pass

    return "\n".join(edited_content_lines).strip()
