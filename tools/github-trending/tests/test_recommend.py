import unittest

from recommend import recommend


class TestRecommend(unittest.TestCase):
    def test_ai_topic(self):
        p = {"name": "llm-tool", "description": "local LLM runner", "language": "Python", "topics": ["llm", "ai"]}
        self.assertIn("AI", recommend(p))

    def test_python_tooling(self):
        p = {"name": "pytest-helper", "description": "test helpers", "language": "Python", "topics": ["testing"]}
        self.assertIn("Python 技术栈", recommend(p))

    def test_document_tooling(self):
        p = {"name": "pdf-inspector", "description": "PDF inspection and text extraction", "language": "Rust", "topics": []}
        self.assertIn("文档/办公处理方向", recommend(p))


if __name__ == "__main__":
    unittest.main()
