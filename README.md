# Slow-Blade

Slow-Blade is an agentic penetration testing and reconnaissance CLI that runs commands inside a Kali-based Docker container.
This is just a fun, novelty project and personal exercise that I figured I'd share.
I recommend checking out [github.com/0xSteph/pentest-ai-agents](https://github.com/0xSteph/pentest-ai-agents) if you need something serious.
With that being said, this has proven to be somewhat effective for busywork like active recon and attack surface mapping.

-----

`(Tested on Windows 11 / Docker Desktop - RTX 2080 SUPER w/ qwen3:8b)`

> [!CAUTION]
> *This is not meant to be used for illegal activity, and should only be used in a sandbox or for controlled CTF excercises. I, as the developer, hold no responsibility for how you use this.*

<img width="603" height="415" alt="image" src="https://github.com/user-attachments/assets/43831cf5-d1bf-4b82-9106-c0ba08bf0350" />

## Install

First, make sure you have [Ollama](https://ollama.com/download) installed.

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

If you want to see the model's reasoning while it works, enable `--show-thinking`:

```bash
slowblade --prompt "Do some recon on mysandboxed.website" --show-thinking
```

You can also tune the model with `--model-options` and cap the tool loop with `--max-iterations`:

```bash
slowblade --prompt "Do some recon on mysandboxed.website" --model qwen3:8b --docker-container kali --model-options '{"temperature": 0.5}' --max-iterations 20 --show-thinking
```

## Model Flow

```mermaid
flowchart TD
    A[User passes prompt via CLI] --> B[SlowBladeCLI parses args]
    B --> C[PenTestAgent initializes]
    C --> D[System prompt + user prompt loaded into message history]
    D --> E[LLM call via Ollama chat]
    E --> F{Does the model request a tool call?}
    F -- No --> G{Has the model produced a sufficient answer or should the engagement continue?}
    G -- Continue --> E
    G -- Final answer --> H[Return final response to user]
    F -- Yes --> I[execute_tool]
    I --> J[run_shell_command]
    J --> K[Docker exec in Kali container]
    K --> L[Command output captured]
    L --> M[Tool result appended to model context]
    M --> E
    E --> N{Max iterations reached or engagement complete?}
    N -- Complete --> H
    N -- Continue --> E
```
