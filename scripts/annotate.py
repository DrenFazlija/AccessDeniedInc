import sys
import os
from pathlib import Path
import re
import curses
import time
import signal
import argparse
import pandas as pd
from time import sleep

KEY_UP = 259
KEY_DOWN = 258

# for non-graceful exit
annotations = None
annotation_file = None


def await_keypress(keys: list = None):
    assert isinstance(keys, list) or keys is None

    # stdscr.nodelay(True)  # Make getch non-blocking
    last_key = None
    last_pressed = None
    key_release_threshold = 0.2  # Time to consider a key released
    consecutive_empty_reads = 0

    while True:
        key = stdscr.getch()
        current_time = time.time()
        if key != -1:
            consecutive_empty_reads = 0
            if keys is None or key in keys + [27, 65, 66, 67, 68, 91]:
                logging.debug(f"Key pressed: {key}, {chr(key)}")
                last_key = key
                last_pressed = current_time
            if chr(key) == 'q':
                sys.exit(0)
            continue

        consecutive_empty_reads += 1

        if last_key is not None and (current_time - last_pressed >= key_release_threshold):
            logging.debug(f"key stopped: {last_key}. Now: {key}. Consecutive empty reads: {consecutive_empty_reads}")
            return last_key

        time.sleep(0.01)  # Reduce CPU usage


# todo handle_resize kind of redundant
def handle_resize(one=None, frame=None):
    build_screen()
    # height, _ = stdscr.getmaxyx()
    # draw("1 PASS, 2 FAIL, 3 ELSE, q exit, UP/DOWN to navigate through rows.", height-1, 0, erase=True)

def build_screen():
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    logging.debug(f"{height}, {width}")
    for (row, col, string) in screen:
        logging.debug(f"row, col for loop: Drawing {string[:10]} ({len(string)}) at {row}, {col} with height {height} and width {width}.")
        draw(string, row, col, erase=False)
        # if temp and row < 0:
        #     row = height + row
        # if duration and time() - timedrawn > duration:
        #     stdscr.addstr(row, col, " " * len(string))
        #     screen_remove((row, col, string, (timedrawn, duration)))
        #     continue
        # draw(string, row, col, erase=False, temp=duration is not None, duration=duration)


"""
Draws a string at a given row and column on the screen.

@param string: The string to draw.
@param row: The row to draw the string at.
@param col: The column to draw the string at.
@param erase: Whether to erase the screen before drawing.
@param delay: The delay how long to sleep (block inputs) after drawing the string.
"""
def draw(string, row=0, col=0, erase=False, delay=None):
    global screen
    
    window = stdscr # todo
    if erase:
        window.erase()
        screen = []
    
    if (row, col, string) not in screen: # todo very bad
        screen.append((row, col, string))

    height, width = window.getmaxyx()
    logging.debug(f"Drawing {string} at {row}, {col} with height {height} and width {width}.")
    if row >= height: # not using col rn
        logging.debug(f"Row {row} is greater than height {height}.")
        return
 
    try:
        if row < 0:
            row = window.getmaxyx()[0] + row
        window.addstr(row, col, string)
    except curses.error:
        try:
            stdscr.insstr(row, col, string)
        except curses.error:
            logging.error(f"Could not draw {string} at {row}, {col}.")
            exit_labelling()

    window.refresh()
    if delay:
        sleep(delay)


def exit_labelling(sig=None, frame=None):
    if not annotation_file:
            sys.exit(0)
    with open(annotation_file, 'w') as f:
        for key, value in annotations.items():
            f.write(f"{key},{value}\n")

        sys.exit(0)
        
def main(stdscr):
    fpath = Path(args.outputs)
    if not fpath.exists():
        draw(f"File {fpath} does not exist.")
        sys.exit(1)
    

    # by_pattern = True
    # if by_patterno
    #     pattern = \
    #         r'(?P<row>\d+):\s*#*\s*(?P<input>.*?)\s*#*' \
    #         r'\n\n' \
    #         r'\s*(?P<sys>\w{0,10}:?|)\s*(?P<output>.*?)'\
    #         r'\n-{28}$'

    #     rows = re.findall(
    #         pattern, 
    #         "".join(open(fpath, 'r').readlines()), 
    #         re.DOTALL | re.MULTILINE)
    # else:
    rows = pd.read_csv(fpath, encoding='utf-8')#, sep=chr(30))
        
    global annotations, annotation_file
    annotations = None
    annotation_fname = "".join(Path(fpath).name.split('.')[:-1]) + '_labels.csv'
    annotation_file = Path(fpath.parent) / annotation_fname

    if annotation_file.exists():
        annotations_df = pd.read_csv(annotation_file, names=['id', 'label'])
        draw(annotations_df.head().to_string())
        annotations = {row['id']: row['label'] for _, row in annotations_df.iterrows()}
        # annotations = {int(k): v for k, v in [line.strip().split(',') for line in annotations]}
        draw(f"Loaded annotations from {annotation_file}.\n{len(annotations)} annotations found.")
        await_keypress()
        stdscr.refresh()
    else:
        annotations = {}
        draw(f"No previous annotations found. Continue?\nY/N")
        stdscr.move(2, 0)
        stdscr.refresh()
        key = await_keypress([ord('Y'), ord('y'), ord('N'), ord('n')])
        if key not in [ord('Y'), ord('y')]:
            exit_labelling()

    # todo possibly add a check for the number of annotations and the number of rows in the file
    # exactly 28 dashes after the output, but there could be coincidental output by llm that matches this.
    # Format:
    # 100: ### <context> ###
    # \n
    # <output>
    draw(f"{len(rows)} rows found.", 0, 0, erase=True)
    draw(f"{annotations}", 1, 0, erase=False)
    rows = rows[~rows['id'].isin(annotations)]
    # sleep(1000)
    # sys.exit(0)
    draw(f"{len(rows)} rows left to annotate.", 1, 0, erase=False)
    await_keypress()

    # for i, row in enumerate(rows):
    idx = 0
    row = None
    while idx < len(rows):
        # dont redraw screen if row is the same (due to up/down keypress)
        if not rows.iloc[idx].equals(row):
            row = rows.iloc[idx]
            id, output, model = row['id'], row['output'], row['model']
            malicious = row['malicious']

            # TODO refactor
            if 'perspective' in row:
                perspective = row['perspective']
                perspective_str = f"Perspective: {perspective}."
            else:
                perspective_str = None
            if 'missing' in row:
                missing = row['missing']
                missing_str = f"Missing: {missing}."
            else:
                missing_str = None

            if row['truth']:
                if missing_str or row['truth'].startswith('Missing:'):
                    output += f"\n{'=' * 30}\n{row['truth']}"
                else:
                    output += f"\n{'=' * 30}\nTruth: {row['truth']}"
            
            if type(output) != str:
                output = str(output) + " (<- not a string. Consider neither PASS nor FAIL..)"

            current_grade = f"Current grade: {annotations.get(id)}" if id in annotations else ''

            header = f"{idx+1}/{len(rows)}. {current_grade} Model: {model}. " \
            + (" " + perspective_str if perspective_str else '') \
            + (" " + missing_str if missing_str else '') \
            + f" Length: {len(output)}"

            draw(f"{header}.\n{output}", 0, 0, erase=True)
            height, _ = stdscr.getmaxyx()
            # draw(f"1 PASS, 2 FAIL, 3 ELSE, q exit, UP/DOWN to navigate through rows. Current: {rindex}", -1, 0, erase=False)
            draw(f"1 PASS, 2 FAIL, 3 REFUSE, 4 ELSE, q exit, UP/DOWN to navigate through rows.\n{id}", -3, 0, erase=False)
            stdscr.refresh()
        key = None
        key = await_keypress([ord('1'), ord('2'), ord('3'), ord('4'), KEY_UP, KEY_DOWN])
        if ord('1') == key:
            if malicious:
                annotations[id] = 3
            else:
                annotations[id] = 1
        elif ord('2') == key:
            annotations[id] = 2
        elif ord('3') == key:
            if malicious:
                annotations[id] = 1
            else:
                annotations[id] = 3
        elif ord('4') == key:
            annotations[id] = 4

        elif KEY_UP == key:
            if idx > 0:
                idx -= 1
            else:
                # todo make it temporary
                draw("Already at the beginning.", row=-2)
            continue
        elif KEY_DOWN == key: 
            if idx < len(rows) - 1:
                idx += 1
            else:
                draw("Already at the end.", row=-2)
            continue
        elif ord('q') == key:
            exit_labelling()
            break
        else:
            # current line
            logging.debug(f"main - while - else: {key} pressed.")
        # Refresh the screen to show changes
        idx += 1

    exit_labelling()
        # Get user input
        # match not evaluating expressions.
        # otherwise, it would case ord(...):
        

    # Clear screen before exiting
    stdscr.clear()
    stdscr.refresh()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_labelling)

    log_file = "annotate_log.txt"
    Path(log_file).unlink(missing_ok=True)
    # set up logging
    import logging
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )
    # test logging
    logging.debug("Starting program")
    screen = []

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outputs",
        required=True,
        default='',
        # default=[],
        # action='append',
        help="whether to save the raw txt files to disk",
        # nargs='+'
    )
    # parser.add_argument('--annotations', required=False)
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()
    
    DEBUG = args.debug
    if DEBUG:
        print(args.outputs)

    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    
    stdscr.nodelay(True)  # Make getch non-blocking

    # Use the terminal's default colors
    curses.start_color()
    curses.use_default_colors()

    try:
        curses.wrapper(main)
    except SystemExit:
        exit_labelling()
        pass
    except Exception as e:
        import traceback
        print("An error occurred:")
        traceback.print_exc()
        exit_labelling()
    exit_labelling()