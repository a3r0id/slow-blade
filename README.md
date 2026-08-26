# Slow-Blade

Slow-Blade is an agentic penetration testing and reconnaissance CLI that runs commands inside a Kali-based Docker container.
This is just a fun, novelty project and personal exercise that I figured I'd share - I recommend checking out [github.com/0xSteph/pentest-ai-agents](https://github.com/0xSteph/pentest-ai-agents) if you need something serious.

*This is not meant to be used for illegal activity, and should only be used in a sandbox or for controlled CTF excercises.*

*I, as the developer, hold no responsibility for how you use this.*

## Install

[Install Ollama](https://ollama.com/download), then,

From the project root:

```bash
python -m pip install -e .
```

## Usage

```bash
slowblade --help
slowblade --prompt "Do some recon on mysandboxed.website"
```

You can also override the model and container:

```bash
slowblade --prompt "Do some recon on mysandboxed.website" --model qwen3:8b --docker-container kali
```
