# src/ai_processor.py
import json
import asyncio # Keep asyncio for consistency with the rest of the async workflow

# --- IMPORTANT: No LLM API key needed for this simulated version ---
# We are intentionally NOT importing openai or any other LLM library here.

async def ai_spin_chapter(chapter_text: str, current_iteration: int = 1) -> str:
    """
    SIMULATED: Applies an AI-driven "spin" to the chapter text.
    In a real scenario, this would use an LLM. Here, it simply adds a prefix
    and suffix to simulate "spinning" the content.
    """
    print(f"SIMULATED AI Writer: Spinning chapter (Iteration {current_iteration})...")
    spun_text = f"[[SIMULATED AI Spun Version - Iteration {current_iteration}]]\n" \
                f"A creatively rephrased passage based on the original content follows:\n\n" \
                f"{chapter_text}\n\n" \
                f"[[End of SIMULATED AI Spun Version]]"
    print("SIMULATED AI Writer: Chapter spun successfully.")
    await asyncio.sleep(0.5) # Simulate processing time
    return spun_text

async def ai_review_chapter(original_text: str, spun_text: str, iteration: int = 1) -> dict:
    """
    SIMULATED: An AI Reviewer checks the spun chapter.
    In a real scenario, this would use an LLM. Here, it provides
    generic feedback and scores to mimic a review.
    """
    print(f"SIMULATED AI Reviewer: Reviewing spun chapter (Iteration {iteration})...")
    # Simulate different review outcomes for varied testing
    # The 'simulated_review' flag indicates this is not a real LLM output.
    if "creatively rephrased passage" in spun_text.lower():
        fidelity_score = 7 + (iteration % 3)
        readability_score = 8 + (iteration % 2)
        grammar_score = 9
        originality_score = 7 + (iteration % 3)
        feedback = "SIMULATED FEEDBACK: The spun content shows good creative effort and largely retains the core message. Some areas could be more concise."
        suggestions = "SIMULATED SUGGESTIONS: Consider condensing overly verbose sentences. Ensure all original nuances are preserved."
    else:
        fidelity_score = 5
        readability_score = 6
        grammar_score = 7
        originality_score = 4
        feedback = "SIMULATED FEEDBACK: The spun content deviates slightly from the original or lacks sufficient 'spin'. Basic errors might be present."
        suggestions = "SIMULATED SUGGESTIONS: Reread the original carefully. Focus on rephrasing more actively and creatively."

    review_data = {
        "fidelity_score": fidelity_score,
        "readability_score": readability_score,
        "grammar_score": grammar_score,
        "originality_score": originality_score,
        "feedback": feedback,
        "suggestions": suggestions,
        "simulated_review": True # This flag indicates it's a simulated review
    }
    print("SIMULATED AI Reviewer: Chapter reviewed successfully.")
    await asyncio.sleep(0.5) # Simulate processing time
    return review_data

# Example usage for testing this module independently
async def main_ai_test():
    sample_original_text = "The quick brown fox jumps over the lazy dog. This is a classic sentence, often used to display fonts because it contains all letters of the alphabet. It is simple, yet effective."
    sample_spun_text = "A nimble russet canine vaulted over a sluggish hound. This timeless expression serves as an excellent pangram, showcasing every letter of the English alphabet with remarkable brevity and clarity."

    print("\n--- SIMULATED AI Spin Test ---")
    spun_result = await ai_spin_chapter(sample_original_text)
    print(f"Spun Text: {spun_result}")

    print("\n--- SIMULATED AI Review Test ---")
    review_result = await ai_review_chapter(sample_original_text, spun_result)
    print(f"Review Result: {json.dumps(review_result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main_ai_test())
