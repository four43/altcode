# altcode: A character selector for Linux
**_Emojis and special character selection via `fzf` and `rofi`, a modern alt-code alternative 😀_** 

**Forked from [fdw/rofimoji](https://github.com/fdw/rofimoji) to provide a more linux/shell focused and extensible version of rofimoji that is simplified and context aware.**

## Features:

 * **Context Aware** - Uses fzf and stdout in CLI enviornments, rofi and xdotool in GUIs.
 * **Extensible** - Special Characters are read from collections in `./altcode.d` directory. Extend the packaged lists or add your own.
 * **Simple** - Minimal common dependencies, just a `bash` script.
 * **Self Update** - Need new emojis? Install the dev python3 dependencies and run the `update_emojis.py` to get the latest list from [the official emoji list](https://unicode.org/emoji/charts-12.0/full-emoji-list.html)
 * **Built in Emojis, Ascii Faces, and Special Characters** - 😸 (☞ ͡° ͜ʖ ͡°)☞ °F ≤
 
## Usage:
```bash
altcode -o|--output [xdotool|clipboard|stdout|-] -s|--selector [fzf|rofi] -t|--skin-tone [neutral|light|medium-light|moderate|dark-brown|black]

By default, will prompt a user to select an special character to copy to the clipboard using fzf if in a terminal, or rofi in a gui.

where:
    Options:
        -o|--output (optional) - Instead of outputting to stdout, output to one of: xdotool (auto type), clipboard, or stdout, -
        -s|--selector (optional) - Uses fzf for CLI environments or rofi for GUIs. Override by specifying one of: fzf, rofi
        -t|--skin-tone (optional) A skin to to apply to select emojis: neutral, light, medium-light, moderate, dark-brown, black
```

Examples:

 1) From a terminal: `./altcode | sed -e 's/^/I feel:/'`
 1) Prompt from rofi: `./altcode -s rofi`
 1) Updating emoji list: `mkdir -p .venv && pipenv install --dev && ./update_emojis.py && rm -rf .venv`

## Todo
 1) Create a better list of emoji modifiers and apply skin tones to more complex emojis, like gender occupations.
 1) xdotool only works in some places?
