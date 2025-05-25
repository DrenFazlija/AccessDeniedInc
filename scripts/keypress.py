import curses
import time
import logging
import sys


def await_keypress(keys: list = None):
    assert isinstance(keys, list) or keys is None

    # stdscr.nodelay(True)  # Make getch non-blocking
    last_key = None
    last_pressed = None
    key_repeat_delay = 0.05  # Adjust this value to change key repeat rate
    key_release_threshold = 0.1  # Time to consider a key released
    consecutive_empty_reads = 0
    empty_read_threshold = 50  # Number of consecutive -1 reads to consider key released
    
    while True:
        key = stdscr.getch()
        current_time = time.time()
        # if key != -1:
        #     logging.debug(f"registered: {key}.")
        logging.debug(f"registered: {key}.")

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

        if last_key is not None and (
            (current_time - last_pressed >= 0.5) 
        ):
            # (consecutive_empty_reads >= empty_read_threshold)
        # ):
            logging.debug(f"key stopped: {last_key}. Now: {key}. Consecutive empty reads: {consecutive_empty_reads}. Time: {current_time - last_pressed}")
            return last_key

        # time.sleep(0.01)  # Reduce CPU usage

# logging
import logging
log_file = 'keypress.log'
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

if __name__ == "__main__":
    stdscr = curses.initscr()
    stdscr.clear()
    stdscr.addstr(0, 0, "Press a key!")
    stdscr.refresh()
    stdscr.nodelay(True)
    r = 0
    pressed = 0
    while True:
        x = await_keypress()
        stdscr.addstr(4, 0, f"Key pressed: {x} Sum: {pressed}")

        # stdscr.addstr(r, 0, f"Key pressed: {x} Sum: {pressed}")
        stdscr.refresh()
        r = ((r + 1) % 15) + 4
        pressed += 1
