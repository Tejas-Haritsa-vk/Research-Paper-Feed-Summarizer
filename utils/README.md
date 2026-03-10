# Utilities Documentation

This directory contains utility modules for the Research Paper Agent, handling everything from content generation to database management.

## Modules

### Content & Newsletter
- **`newsletter.py`**: Core logic for generating HTML and Text newsletters. Uses distinct styling depending on the presence of a TL;DR.
- **`content_generation.py`**: Orchestrates LLM calls to generate summarized content (TL;DRs) for newsletters.
- **`render_templates.py`**: Helper functions to format content for different platforms (Discord webhooks, HTML emails).

### Data Management
- **`subscriber_manager.py`**: Manages the SQLite-based subscriber database (`subscribers.db`). Handles adding/removing users and updating topic preferences.
- **`feed_state.py`**: Interfaces with the main database to track which papers have been sent (to avoid duplicates) and fetches "unsent" batches.
- **`deduplication.py`**: Logic for identifying and merging duplicate paper entries from different sources.
- **`paper_utils.py`**: `PaperUtils` class for handling PDF downloads, filename sanitization, and text extraction.
- **`datetime_utils.py`**: formatting and parsing dates.

### Scripts
- **`send_feed.py`**: A standalone script that orchestrates the entire "send newsletter" workflow: fetching unsent papers, generating personalized emails, and marking successful sends in the DB.

### LLM Helpers
- **`jsonify_llm_response.py`**: Utility to parse and validate JSON responses from LLMs.
