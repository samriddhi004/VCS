#!/usr/bin/env python3
"""
AI-powered Git diff summarizer.
Analyzes unstaged changes and generates natural-language summaries using Gemini API.
"""

import os
import sys
import subprocess
import google.generativeai as genai


def run_git_command(args):
    """
    Execute a git command and return its output.
    
    Args:
        args: List of command arguments (e.g., ['git', 'diff'])
    
    Returns:
        str: Command output or empty string on error
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        return ""


def get_unstaged_diff():
    """
    Get the diff of unstaged changes.
    
    Returns:
        str: Git diff output or empty string if no changes
    """
    return run_git_command(['git', 'diff'])


def generate_diff_summary(diff_text):
    """
    Generate a natural-language summary of git diff using Gemini API.
    
    Args:
        diff_text: The git diff output
    
    Returns:
        str: Natural language summary of changes
    """
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Construct the prompt
    prompt = f"""You are a code review assistant. Analyze the following git diff and generate a clear, concise natural-language summary.

Your summary should explain:
1. What files were changed
2. What type of changes were made (bug fix, new feature, refactoring, documentation, configuration, etc.)
3. A brief description of the specific changes in each file

Format your response as:
- Start with an overview sentence
- List each file with bullet points explaining changes
- Be specific but concise
- Use technical terms appropriately but keep it readable

GIT DIFF:
{diff_text}

Summary:"""
    
    try:
        # Generate the summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        sys.exit(1)


def format_output(summary):
    """
    Format and display the summary with nice visual separators.
    
    Args:
        summary: The AI-generated summary text
    """
    print("\n" + "="*80)
    print("DIFF SUMMARY")
    print("="*80)
    print()
    print(summary)
    print()
    print("="*80)


def main():
    """Main entry point for the CLI tool."""
    print("AI-Powered Git Diff Summarizer\n")
    
    # Step 1: Get unstaged changes
    print("📋 Analyzing unstaged changes...")
    diff = get_unstaged_diff()
    
    if not diff:
        print("\n  No unstaged changes found.")
        print(" Make some changes to your files, then run this tool to see a summary.")
        print(" To see staged changes, use: git diff --cached")
        sys.exit(0)
    
    # Count lines and files changed
    diff_lines = diff.splitlines()
    files_changed = len([line for line in diff_lines if line.startswith('diff --git')])
    
    print(f"✓ Found {files_changed} file(s) with {len(diff_lines)} lines of changes\n")
    
    # Step 2: Generate summary using AI
    print(" Generating summary with AI...\n")
    summary = generate_diff_summary(diff)
    
    # Step 3: Display the summary
    format_output(summary)


if __name__ == '__main__':
    main()