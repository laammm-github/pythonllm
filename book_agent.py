"""
Reading Intelligent Agent

A lightweight book assistant prototype.
Features:
- Book note management
- Chapter summarization interface
- Q&A over reading notes
- Learning plan generation

The LLM backend can be replaced by OpenAI/Ollama/local models.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Book:
    title: str
    author: str
    notes: List[str] = field(default_factory=list)


class ReadingAgent:
    def __init__(self):
        self.books = {}

    def add_book(self, title: str, author: str):
        self.books[title] = Book(title, author)
        return f"Added book: {title}"

    def add_note(self, title: str, note: str):
        if title not in self.books:
            raise ValueError("Book not found")
        self.books[title].notes.append(note)

    def summarize(self, title: str):
        book = self.books[title]
        return {
            "book": book.title,
            "author": book.author,
            "summary": " ".join(book.notes),
            "key_points": book.notes,
        }

    def ask(self, title: str, question: str):
        book = self.books[title]
        context = " ".join(book.notes)
        return f"Based on notes: {context}\nQuestion: {question}"

    def learning_plan(self, title: str, days: int = 7):
        return [f"Day {i}: Read and reflect on {title}" for i in range(1, days + 1)]


if __name__ == "__main__":
    agent = ReadingAgent()
    agent.add_book("AI Agent", "Unknown")
    agent.add_note("AI Agent", "Agents combine reasoning, tools and memory.")
    print(agent.summarize("AI Agent"))
