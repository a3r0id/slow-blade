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

        async def noop_spinner(*args, **kwargs):
            return

        agent.spinner_task = noop_spinner

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

    def test_complete_engagement_writes_report_and_stops_loop(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import asyncio
        import json
        import main

        with TemporaryDirectory() as tmp:
            agent = PenTestAgent(max_iterations=3)
            agent.tools.reports_dir = Path(tmp)

            tool_call = SimpleNamespace(
                function=SimpleNamespace(
                    name="complete_engagement",
                    arguments={
                        "after_action_report": "# After-Action Report\n\nEngagement wrapped.",
                        "final_closing_message": "Wrapped up.",
                        "report_filename": "aar.md",
                    },
                )
            )

            def make_message(content, tool_calls=None):
                return SimpleNamespace(
                    tool_calls=tool_calls,
                    content=content,
                    thinking=None,
                    model_dump_json=lambda: json.dumps({"content": content}),
                )

            response = SimpleNamespace(message=make_message("finishing", [tool_call]))
            agent.messages = [{"role": "user", "content": "hello"}]
            agent._responses = [response]

            async def noop_spinner(*args, **kwargs):
                return

            agent.spinner_task = noop_spinner

            original_chat = main.chat
            main.chat = lambda *args, **kwargs: agent._responses.pop(0)
            try:
                result = asyncio.run(agent.get_response())
            finally:
                main.chat = original_chat

            self.assertEqual(result, "Engagement completed.")
            self.assertTrue(agent.tools.is_complete)
            self.assertTrue((Path(tmp) / "aar.md").exists())


class CompleteEngagementTests(unittest.TestCase):
    def test_empty_report_does_not_complete(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from tools import Tools

        with TemporaryDirectory() as tmp:
            tools = Tools(reports_dir=tmp)
            result = tools.complete_engagement(after_action_report="   ")

            self.assertFalse(tools.is_complete)
            self.assertIsNone(tools.last_report_path)
            self.assertIn("after_action_report is required", result)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_writes_markdown_report_and_completes(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from tools import Tools

        report = """# After-Action Report

## Engagement Overview
Target: example.test

## Executive Summary
No exploitable findings.

## Methodology and Tools Used
curl, nmap

## Chronological Actions Taken
1. Resolved DNS
2. Fetched robots.txt

## Findings
None.

## Recommendations
Keep monitoring.

## Limitations and Residual Risk
Passive recon only.
"""

        with TemporaryDirectory() as tmp:
            tools = Tools(reports_dir=tmp)
            result = tools.complete_engagement(
                after_action_report=report,
                final_closing_message="Done.",
                report_filename="crawl-maze.md",
            )

            self.assertTrue(tools.is_complete)
            report_path = Path(tools.last_report_path)
            self.assertEqual(report_path.name, "crawl-maze.md")
            self.assertTrue(report_path.exists())
            contents = report_path.read_text(encoding="utf-8")
            self.assertIn("# After-Action Report", contents)
            self.assertIn("Target: example.test", contents)
            self.assertIn("Done.", result)
            self.assertIn(str(report_path), result)

    def test_report_filename_cannot_escape_reports_dir(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from tools import Tools

        with TemporaryDirectory() as tmp:
            tools = Tools(reports_dir=tmp)
            tools.complete_engagement(
                after_action_report="# After-Action Report\n\nScoped finding.",
                report_filename="../escape.md",
            )

            report_path = Path(tools.last_report_path)
            self.assertEqual(report_path.parent, Path(tmp))
            self.assertEqual(report_path.name, "escape.md")


if __name__ == "__main__":
    unittest.main()
