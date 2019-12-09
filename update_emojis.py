from dataclasses import dataclass
from functools import reduce

import os

from typing import List, Set, Dict

import logging
import requests
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import XPath

logger = logging.getLogger(__name__)


@dataclass
class Emoji:
    char: str
    code_points: List[str]
    name: str


def fetch_emoji_html() -> BeautifulSoup:
    max_tries = 5
    for i in range(max_tries):
        logger.info('Downloading emojis... try %s' % (i + 1))
        data = requests.get(
            'https://unicode.org/emoji/charts-12.0/full-emoji-list.html',
            timeout=120
        )  # type: requests.Response
        if data:
            break

    if not data:
        logger.error('Could not fetch emoji data. Try again later or use another URL.')
        exit(10)
    return BeautifulSoup(data.content, 'lxml')


def fetch_mod_emojis() -> BeautifulSoup:
    logger.info('Downloading list of human emojis...')

    max_tries = 5
    for i in range(max_tries):
        logger.info('Downloading emojis with modifiers... try %s' % (i + 1))
        data = requests.get(
            'https://unicode.org/emoji/charts-12.0/full-emoji-modifiers.html',
            timeout=120
        )  # type: requests.Response
        if data:
            break

    if not data:
        logger.error('Could not fetch emoji data. Try again later or use another URL.')
        exit(10)
    return BeautifulSoup(data.content, 'lxml')


def extract_from_html(html: BeautifulSoup) -> List[Emoji]:
    emojis = []

    for row in html.find('table').find_all('tr'):
        if row.th:
            continue
        emoji = str(row.find('td', {'class': 'chars'}).string)
        code_points = row.find('td', {'class': 'code'}).string.split(' ')
        description = row.find('td', {'class': 'name'}).string.replace('⊛ ', '')

        emojis.append(Emoji(
            char=emoji,
            code_points=code_points,
            name=description))

    return emojis


def extract_emojis_from_line(line: str) -> List[chr]:
    emoji_range = line.split(';')[0].strip()
    try:
        (start, end) = emoji_range.split('..')
        emojis = []
        for char in range(int(start, 16), int(end, 16) + 1):
            emojis.append(chr(char))
        return emojis
    except ValueError:
        return [chr(int(emoji_range, 16))]


def fetch_annotations() -> Dict[chr, List[str]]:
    print('Downloading annotations')

    data = requests.get(
        'https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/en.xml',
        timeout=60
    )  # type: requests.Response

    xpath = XPath('./annotations/annotation[not(@type="tts")]')
    return {element.get('cp'): element.text.split(' | ') for element in
            xpath(etree.fromstring(data.content))}


def write_file(all_emojis: List[Emoji], human_emojis: Set[chr], annotations: Dict[chr, List[str]]):
    print('Writing collected emojis to file')
    python_file = open('emojis.py', 'w')
    python_file.write('emoji_list="""')

    for entry in compile_entries(all_emojis, annotations):
        python_file.write(entry + "\n")

    python_file.write('"""\n\n')

    python_file.write('skin_tone_selectable_emojis={\'')
    python_file.write('\', \''.join(human_emojis))
    python_file.write('\'}\n')

    python_file.close()


def compile_entries(emojis: List[Emoji], annotations: Dict[chr, List[str]]) -> List[str]:
    annotated_emojis = []
    for emoji in emojis:
        if emoji.char in annotations:
            entry = f"{emoji.char} | {emoji.name} <small>({', '.join(annotations[emoji.char])})</small>"
        else:
            entry = f"{emoji.char} | {emoji.name}"

        annotated_emojis.append(entry)

    return annotated_emojis


def write_file(all_emojis: List[Emoji], human_emojis: List[Emoji], annotations: Dict[chr, List[str]]):
    logger.info('Writing collected emojis to files')
    script_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(script_dir, 'emojis.d', 'emojis.txt'), 'w') as output_file:
        for entry in compile_entries(all_emojis, annotations):
            output_file.write(f"{entry}\n")

    with open(os.path.join(script_dir, 'emojis.d', 'emoji_modifiers.meta'), 'w') as output_file:
        for emoji in human_emojis:
            output_file.write(f"{emoji.char[0]}\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    emoji_html = fetch_emoji_html()
    mod_emoji_html = fetch_mod_emojis()

    emoji_list = extract_from_html(emoji_html)
    mod_emojis_full = extract_from_html(mod_emoji_html)


    def prune_human_emoji_list(current: List[Emoji], item: Emoji):
        """
        Parsing for this could be much improved as it's typically [gender][skin-tone][occupation] which we totally
        just ignore right now
        """
        if len(item.code_points) == 2:
            for current_emoji in current:
                if item.code_points[0] == current_emoji.code_points[0]:
                    break
            else:
                current.append(item)
        return current

    human_emoji_list = reduce(prune_human_emoji_list, mod_emojis_full, [])
    write_file(emoji_list, human_emoji_list, fetch_annotations())
