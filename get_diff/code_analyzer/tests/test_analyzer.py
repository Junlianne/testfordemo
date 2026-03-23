import unittest
from unittest.mock import patch, MagicMock
from core.analyzer import Analyzer

class TestAnalyzer(unittest.TestCase):
    @patch('core.analyzer.OpenAI')
    def test_analyze_context(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test Context Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = Analyzer(api_key="test_key", max_retries=1)
        pr_details = {"title": "Add feature", "description": "Adds a new feature"}
        result = analyzer.analyze_context("diff content", pr_details)
        
        self.assertEqual(result, "Test Context Response")
        mock_client.chat.completions.create.assert_called_once()

    @patch('core.analyzer.OpenAI')
    def test_analyze_for_dev_stream(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock(delta=MagicMock(content="Chunk 1 "))]
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock(delta=MagicMock(content="Chunk 2"))]
        
        mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]

        analyzer = Analyzer(api_key="test_key", max_retries=1)
        pr_details = {"title": "Fix bug", "description": "Fixes a critical bug"}
        
        result_stream = analyzer.analyze_for_dev("diff content", pr_details, "Context", stream=True)
        result = "".join(list(result_stream))
        
        self.assertEqual(result, "Chunk 1 Chunk 2")

if __name__ == '__main__':
    unittest.main()
