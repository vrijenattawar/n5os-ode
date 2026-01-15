---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Contributing to N5OS-Ode

Thank you for your interest in contributing to N5OS-Ode!

## Getting Started

1. Fork the repository
2. Run the BOOTLOADER prompt in your Zo workspace
3. Make your changes
4. Test locally
5. Submit a pull request

## Types of Contributions

### Prompts
New workflows should be added as `.prompt.md` files in `/Prompts/`. Include:
- Clear description in YAML frontmatter
- Step-by-step instructions
- Example usage

### Scripts
Python utilities go in `N5/scripts/`. Requirements:
- CLI interface with `--help`
- Non-interactive operation
- Proper error handling

### Documentation
Documentation improvements are always welcome. When updating docs:
- Keep language clear and concise
- Include examples where helpful
- Update any affected cross-references

## Code Style

- Python: Follow PEP 8
- Markdown: Use consistent header levels, one sentence per line for diffs
- YAML: 2-space indentation

## Pull Request Process

1. Update documentation for any changed functionality
2. Test your changes locally
3. Write clear commit messages
4. Reference any related issues

## Questions?

Open an issue for questions or discussion.

