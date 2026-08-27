from time import sleep
from rich.live import Live
from rich.text import Text

def play_blade_frames():

    frames: list[str] = []

    for i in range(1, 11):
        with open(f"data/frames/{i}.ascii", encoding="utf-8") as f:
            frames.append(f.read())

    with Live(
        "",
        refresh_per_second=10,
        transient=True,
    ) as live:

        for frame in frames:
            live.update(Text(frame))
            sleep(0.25)

        frames.reverse()

        for frame in frames:
            live.update(Text(frame))
            sleep(0.25) 

    print()