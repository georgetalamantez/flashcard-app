import os
import json
import re
import argparse

def convert_md_to_json(md_file_path, json_file_path):
    """Converts a Markdown flashcard file to JSON format."""
    if not os.path.exists(md_file_path):
        print(f"Error: {md_file_path} not found.")
        return

    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expression to match flashcards
    # Format: 
    # **Question:** [Question text]
    # **Answer:** [Answer text]
    pattern = r"\*\*Question:\*\*\s*(.*?)\s*\n\s*\*\*Answer:\*\*\s*(.*?)(?=\n\s*\d+\.\s+\*\*Question:\*\*|\n\s*###|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    flashcards = []
    for q, a in matches:
        flashcards.append({
            "question": q.strip(),
            "answer": a.strip()
        })

    if not flashcards:
        # Try an alternative pattern if the first one fails
        pattern_alt = r"Question:\s*(.*?)\s*\n\s*Answer:\s*(.*?)(?=\n\s*Question:|\Z)"
        matches_alt = re.findall(pattern_alt, content, re.DOTALL)
        for q, a in matches_alt:
            flashcards.append({
                "question": q.strip(),
                "answer": a.strip()
            })

    if flashcards:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, indent=2)
        print(f"Successfully converted {len(flashcards)} flashcards to {json_file_path}")
    else:
        print(f"No flashcards found in {md_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown flashcards to JSON")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("output", help="Output JSON file")
    args = parser.parse_args()
    
    convert_md_to_json(args.input, args.output)
