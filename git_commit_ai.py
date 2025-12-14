"""
AI-powered Git commit message generator.
Analyzes staged changes and generates professional commit messages using Gemini API.
User stages changes → Tool reads diff → Sends to Gemini AI → Gets commit message → User confirms → Git commits
"""

import os
import sys
import subprocess
import google.generativeai as genai


def run_git_command(args):
    """
    Execute a git command and return its output.
    
    Args:
        args: List of command arguments (e.g., ['git', 'diff', '--cached'])
    
    Returns:
        str: Command output or empty string on error
    """
    try:
        result = subprocess.run(
            args,                   #list of cmd parts
            capture_output=True,    #captures stdout(o/p) and stderr(errors)
            text=True,              #returns o/p as string(notBYTES)
            check=True              #raises exception if command fails
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        return ""


def get_staged_diff():
    """
    Get the diff of staged changes(files git add-ed & Last commit(HEAD))
    
    Returns:
        str: Git diff output or empty string if no changes
    """
    return run_git_command(['git', 'diff', '--cached'])


def generate_commit_message(diff_text):
    """
    Generate a commit message using Gemini API based on git diff.
    
    Args:
        diff_text: The git diff output
    
    Returns:
        str: Generated commit message
    """
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Use Gemini 2.5 Flash (free tier)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Construct the prompt
    prompt = f"""You are a Git commit message expert. Analyze the following git diff and generate a concise, professional commit message.

REQUIREMENTS:
- The message must be 50-72 characters long
- Use imperative mood (e.g., "Add feature" not "Added feature")
- Be specific about what changed
- Do not include any explanation, prefix, or formatting
- Return ONLY the commit message text, nothing else

GIT DIFF:
{diff_text}

Commit message:"""
    
    try:
        # Generate the commit message
        response = model.generate_content(prompt)
        message = response.text.strip()
        
        # Remove any quotes or extra formatting the LLM might add
        message = message.strip('"\'').strip()
        
        return message
    except Exception as e:
        print(f"Error generating commit message: {e}", file=sys.stderr)
        sys.exit(1)


def get_user_confirmation(message):
    """
    Display the suggested message and ask for user confirmation.
    
    Args:
        message: The suggested commit message
    
    Returns:
        tuple: (bool, str) - (whether to commit, final message)
    """
    print("\n" + "="*70)
    print("SUGGESTED COMMIT MESSAGE:")
    print("="*70)
    print(f"\n{message}\n")
    print("="*70)
    
    while True:
        choice = input("\n[c]ommit / [e]dit / [a]bort? ").lower().strip()
        
        if choice == 'c':
            return True, message
        elif choice == 'e':
            print("\nEnter your commit message (press Enter when done):")
            edited_message = input("> ").strip()
            if edited_message:
                return True, edited_message
            else:
                print("Empty message, please try again.")
        elif choice == 'a':
            return False, None
        else:
            print("Invalid choice. Please enter 'c', 'e', or 'a'.")


def commit_changes(message):
    """
    Commit staged changes with the provided message.
    
    Args:
        message: The commit message to use
    
    Returns:
        bool: True if commit succeeded
    """
    try:
        subprocess.run(
            ['git', 'commit', '-m', message],
            check=True
        )
        print(f"\n✓ Changes committed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for the CLI tool."""
    print("AI Git Commit Message Generator\n")
    
    # Step 1: Get staged changes
    print("Checking for staged changes...")
    diff = get_staged_diff()
    
    if not diff:
        print("\n⚠ No staged changes found.")
        print("Use 'git add <files>' to stage changes before running this tool.")
        sys.exit(0)
    
    print(f"✓ Found {len(diff.splitlines())} lines of changes\n")
    
    # Step 2: Generate commit message
    print("Generating commit message with AI...")
    commit_message = generate_commit_message(diff)
    
    # Step 3: Get user confirmation
    should_commit, final_message = get_user_confirmation(commit_message)
    
    if not should_commit:
        print("\nX Commit aborted.")
        sys.exit(0)
    
    # Step 4: Commit the changes
    print(f"\nCommitting with message: '{final_message}'")
    commit_changes(final_message)


if __name__ == '__main__':
    main()