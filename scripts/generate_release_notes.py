#!/usr/bin/env python3
"""
Release Notes Generator

Automatically generates release notes from git commits and version information.
"""

import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_commits_since_last_tag(current_tag: str) -> list:
    """Get git commits since the last tag."""
    try:
        # Get the previous tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", f"{current_tag}^"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            last_tag = result.stdout.strip()
        else:
            # No previous tag, get all commits
            last_tag = "HEAD~1000"
        
        # Get commits between last tag and current tag
        result = subprocess.run(
            ["git", "log", f"{last_tag}..{current_tag}", "--pretty=format:%h|%s|%an|%ad", "--date=short"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'date': parts[3]
                    })
        
        return commits
    
    except Exception:
        return []


def categorize_commits(commits: list) -> dict:
    """Categorize commits by type based on conventional commit format."""
    categories = {
        'features': [],
        'fixes': [],
        'docs': [],
        'tests': [],
        'refactor': [],
        'performance': [],
        'ci': [],
        'other': []
    }
    
    for commit in commits:
        message = commit['message'].lower()
        
        if any(keyword in message for keyword in ['feat:', 'feature:', 'add:']):
            categories['features'].append(commit)
        elif any(keyword in message for keyword in ['fix:', 'bug:', 'hotfix:']):
            categories['fixes'].append(commit)
        elif any(keyword in message for keyword in ['doc:', 'docs:', 'documentation:']):
            categories['docs'].append(commit)
        elif any(keyword in message for keyword in ['test:', 'tests:', 'testing:']):
            categories['tests'].append(commit)
        elif any(keyword in message for keyword in ['refactor:', 'refact:', 'cleanup:']):
            categories['refactor'].append(commit)
        elif any(keyword in message for keyword in ['perf:', 'performance:', 'optimize:']):
            categories['performance'].append(commit)
        elif any(keyword in message for keyword in ['ci:', 'build:', 'deploy:']):
            categories['ci'].append(commit)
        else:
            categories['other'].append(commit)
    
    return categories


def get_version_info(tag: str) -> dict:
    """Extract version information from tag."""
    # Remove 'v' prefix if present
    version = tag.lstrip('v')
    
    # Parse semantic version
    version_parts = version.split('.')
    major = version_parts[0] if len(version_parts) > 0 else "1"
    minor = version_parts[1] if len(version_parts) > 1 else "0"
    patch = version_parts[2] if len(version_parts) > 2 else "0"
    
    return {
        'full': version,
        'major': major,
        'minor': minor,
        'patch': patch
    }


def generate_release_notes(tag: str) -> str:
    """Generate release notes for the given tag."""
    version_info = get_version_info(tag)
    commits = get_git_commits_since_last_tag(tag)
    categorized_commits = categorize_commits(commits)
    
    release_date = datetime.now().strftime("%Y-%m-%d")
    
    # Start building release notes
    notes = f"""# Pro-Forma Analytics Tool {version_info['full']}

*Released: {release_date}*

"""
    
    # Add version highlights based on version type
    if version_info['minor'] == "0" and version_info['patch'] == "0":
        # Major release
        notes += """## 🚀 Major Release Highlights

This major release represents a significant milestone in the Pro-Forma Analytics Tool development with substantial new features and improvements.

"""
    elif version_info['patch'] == "0":
        # Minor release
        notes += """## ✨ New Features & Improvements

This release includes new features and enhancements to improve functionality and user experience.

"""
    else:
        # Patch release
        notes += """## 🐛 Bug Fixes & Improvements

This patch release focuses on bug fixes and small improvements.

"""
    
    # Add categorized changes
    if categorized_commits['features']:
        notes += "## 🎉 New Features\n\n"
        for commit in categorized_commits['features']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['fixes']:
        notes += "## 🐛 Bug Fixes\n\n"
        for commit in categorized_commits['fixes']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['performance']:
        notes += "## ⚡ Performance Improvements\n\n"
        for commit in categorized_commits['performance']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['docs']:
        notes += "## 📚 Documentation\n\n"
        for commit in categorized_commits['docs']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['tests']:
        notes += "## 🧪 Testing\n\n"
        for commit in categorized_commits['tests']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['refactor']:
        notes += "## 🔨 Code Improvements\n\n"
        for commit in categorized_commits['refactor']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['ci']:
        notes += "## 🔧 CI/CD & Build\n\n"
        for commit in categorized_commits['ci']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    if categorized_commits['other']:
        notes += "## 📦 Other Changes\n\n"
        for commit in categorized_commits['other']:
            notes += f"- {commit['message']} ({commit['hash']})\n"
        notes += "\n"
    
    # Add installation instructions
    notes += """## 📦 Installation

```bash
# Install from PyPI
pip install pro-forma-analytics-tool

# Or clone and install from source
git clone https://github.com/your-org/pro-forma-analytics-tool.git
cd pro-forma-analytics-tool
pip install -r requirements.txt
```

## 🚀 Quick Start

```bash
# Run the complete DCF workflow demonstration
python demo_end_to_end_workflow.py

# Run the test suite
pytest tests/
```

## 📊 What's Included

- **Complete DCF Engine**: 4-phase workflow with NPV, IRR, and investment recommendations
- **Monte Carlo Simulation**: 500+ scenarios with economic correlations
- **Prophet Forecasting**: Time series forecasting for 11 pro forma parameters
- **Clean Architecture**: Domain-driven design with comprehensive testing
- **Production Ready**: 95%+ test coverage with CI/CD pipeline

"""
    
    # Add compatibility information
    notes += f"""## 🔗 Compatibility

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.13
- **Operating Systems**: Windows, macOS, Linux
- **Dependencies**: See `requirements.txt` for complete list

## 👥 Contributors

Thank you to all contributors who made this release possible!

"""
    
    # Add total commit count
    total_commits = len(commits)
    if total_commits > 0:
        notes += f"**Total commits in this release: {total_commits}**\n\n"
    
    notes += "---\n\n"
    notes += "For detailed technical documentation, see the [documentation folder](docs/) or visit our [User Guide](docs/USER_GUIDE.md)."
    
    return notes


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python generate_release_notes.py <tag>")
        sys.exit(1)
    
    tag = sys.argv[1]
    
    try:
        release_notes = generate_release_notes(tag)
        print(release_notes)
    except Exception as e:
        print(f"Error generating release notes: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()