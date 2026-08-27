import unittest
from types import SimpleNamespace

from main import PenTestAgent, parse_options


class ParseOptionsTests(unittest.TestCase):
    def test_empty_json_defaults_to_empty_dict(self):
        self.assertEqual(parse_options("{}"), {})
        self.assertEqual(parse_options(""), {})

    def test_valid_json_is_parsed(self):
        self.assertEqual(parse_options('{"temperature": 0.5, "top_p": 0.9}'), {
            "temperature": 0.5,
            "top_p": 0.9,
        })

    def test_invalid_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            parse_options('{not valid json}')


class AgentLoopTests(unittest.TestCase):
    def test_complete_engagement_tool_is_available(self):
        agent = PenTestAgent()
        tool_names = [getattr(tool, "__name__", str(tool)) for tool in agent.tools.get_tools_list()]
        self.assertIn("complete_engagement", tool_names)

    def test_show_thinking_prints_thinking_and_content(self):
        import io
        from contextlib import redirect_stdout

        agent = PenTestAgent(show_thinking=True)
        msg = SimpleNamespace(thinking="internal plan", content="final answer")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            agent.agent_message_log(msg)

        output = buffer.getvalue()
        self.assertIn("internal plan", output)
        self.assertIn("final answer", output)

    def test_non_tool_response_does_not_exit_early(self):
        agent = PenTestAgent(max_iterations=2)
        agent.tools.is_complete = False

        def make_message(content):
            return SimpleNamespace(
                tool_calls=None,
                content=content,
                thinking=None,
                model_dump_json=lambda: json.dumps({"content": content}),
            )

        response_1 = SimpleNamespace(message=make_message("still exploring"))
        response_2 = SimpleNamespace(message=make_message("done"))

        agent.messages = [{"role": "user", "content": "hello"}]
        agent._responses = [response_1, response_2]

        def fake_chat(*args, **kwargs):
            return agent._responses.pop(0)

        import json
        import main
        original_chat = main.chat
        main.chat = fake_chat
        try:
            result = __import__('asyncio').run(agent.get_response())
        finally:
            main.chat = original_chat

        self.assertEqual(result, "Maximum agent iterations reached.")


if __name__ == "__main__":
    unittest.main()
