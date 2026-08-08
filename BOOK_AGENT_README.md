# Reading Intelligent Agent

## Vision
A personal AI reading companion that helps users understand, remember and apply books.

## Current Features

- Book collection management
- Reading notes storage
- Summary generation interface
- Question answering over notes
- Personalized reading plan

## Architecture

```
User
 |
 v
Reading Agent
 |
 +-- Memory (book notes)
 |
 +-- Reasoning Engine (LLM)
 |
 +-- Tools (search, summarize, plan)
```

## Future Extensions

1. RAG knowledge base for PDFs and ebooks
2. Vector database memory
3. Knowledge graph of concepts and authors
4. Multi-agent discussion between critic, teacher and learner agents
5. Notion synchronization

## Example Usage

```python
from book_agent import ReadingAgent

agent = ReadingAgent()
agent.add_book('Deep Learning', 'Ian Goodfellow')
agent.add_note('Deep Learning', 'Neural networks learn hierarchical representations.')
print(agent.summarize('Deep Learning'))
```
