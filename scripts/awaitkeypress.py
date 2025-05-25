def ___123___await_keypress(keys: list = None):
    assert isinstance(keys, list) or keys is None

    # stdscr.nodelay(True)  # Make getch non-blocking
    last_key = None
    last_pressed = None
    key_repeat_delay = 0.1  # Adjust this value to change key repeat rate
    key_release_threshold = 0.2  # Time to consider a key released
    consecutive_empty_reads = 0
    empty_read_threshold = 30  # Number of consecutive -1 reads to consider key released

    while True:
        key = stdscr.getch()
        current_time = time.time()
        logging.debug(f"registered: {key}.")

        if key != -1:
            consecutive_empty_reads = 0
            if keys is None or key in keys + [27, 65, 66, 67, 68, 91]:
                logging.debug(f"Key pressed: {key}, {chr(key)}")
                if key != last_key or (current_time - last_pressed) >= key_repeat_delay:
                    last_key = key
                    last_pressed = current_time
            if chr(key) == 'q':
                exit_labelling()
            continue
        
        consecutive_empty_reads += 1

        if last_key is not None and (
            (current_time - last_pressed >= key_release_threshold) and
            (consecutive_empty_reads >= empty_read_threshold)
        ):
            logging.debug(f"key stopped: {last_key}. Now: {key}. Consecutive empty reads: {consecutive_empty_reads}")
            return last_key

        time.sleep(0.01)  # Reduce CPU usage

def _____await_keypress(keys: list = None):
    assert isinstance(keys, list) or keys is None

    stdscr.nodelay(True)  # Make getch non-blocking
    last_key = None
    last_pressed = None
    key_repeat_delay = 0.1  # Adjust this value to change key repeat rate
    was_empty = False # needs to be toggled to True once. Happens, when we read at least ONCE -1. Disallow held down keys from previous iterations.
    while True:
        key = stdscr.getch()
        current_time = time.time()
        logging.debug(f"registered: {key}.")
        if key != -1 and was_empty:  # A key was pressed after not having been pressed
            if keys is None or key in keys + [27, 65, 66, 67, 68, 91]:
                logging.debug(f"Key pressed: {key}, {chr(key)}")
                if key != last_key or (current_time - last_pressed) >= key_repeat_delay:
                    last_key = key
                    last_pressed = current_time
                
        elif last_key is not None and last_pressed and (current_time - last_pressed) >= 0.1:
            logging.debug(f"key stopped: {last_key}. Now: {key}")
            return last_key
        # no key pressed, will only be True once
        elif not was_empty:
            logging.debug(f"First time no key pressed. Registered: {key}. Was empty before: {was_empty}. Will become True now.")
            was_empty = True
            # time.sleep(0.01)


        time.sleep(0.01)  # Reduce CPU usage


def _await_keypress(keys: list = None):
    i = 0
    assert isinstance(keys, list) or keys is None

    stdscr.nodelay(True)  # Make getch non-blocking
    current_time = time.time()
    last_key = None
    last_pressed = None
    while True:
        key = stdscr.getch()
        if key == -1:  # No key pressed
            if last_key is not None and time.time() - last_pressed >= 0.2:
                logging.debug(f"key stopped: {last_key}. Now: {key}")
                stdscr.nodelay(False)  # Reset to blocking mode
                return last_key
            time.sleep(0.05)  # Reduce CPU usage
            continue

        if key == curses.KEY_RESIZE:
            logging.debug(f"Key pressed: {key}")
            if time.time() - current_time > 0.1:
                handle_resize()
                current_time = time.time()
        elif key == ord('q'):
            exit_labelling()
        elif keys is None or key in keys + [27, 65, 66, 67, 68, 91]:
            logging.debug(f"Key pressed: {key}, {chr(key)}")
            if last_key == key:
                continue
            last_key = key
            last_pressed = time.time()



def __await_keypress(keys: list = None):
    assert isinstance(keys, list) or keys is None
    logging.debug("in await_keypress")

    stdscr.nodelay(True)  # Make getch non-blocking
    current_time = time.time()
    last_key = None
    last_pressed = None
    while True:
        key = stdscr.getch()
        if key == -1:  # No key pressed
            if last_key is not None and time.time() - last_pressed >= 0.2:
                stdscr.nodelay(False)  # Reset to blocking mode
                logging.debug(f"key stopped: {last_key}. Now: {key}")
                return last_key
            time.sleep(0.01)  # Reduce CPU usage
            continue

        if key == curses.KEY_RESIZE:
            logging.debug(f"Key pressed: {key}")
            if time.time() - current_time > 0.1:
                handle_resize()
                current_time = time.time()
        elif key == ord('q'):
            exit_labelling()
        elif keys is None or key in keys:
            logging.debug(f"Key pressed: {key}, {chr(key)}")
            if last_key == key:
                continue
            last_key = key
            last_pressed = time.time()
            

    # Ensure we reset to blocking mode if we somehow exit the loop
    stdscr.nodelay(False)



def __backup_await_keypress(keys: list = None, any_key=False):
    assert isinstance(keys, list) or keys is None
    logging.debug(f"in await_keypress")

    # we want to wait for any key except signals like curses.KEY_RESIZE
    if not keys:
        keys = []
        logging.debug(f"in await_keypress: any_key")
        current_time = time()
        while (key := stdscr.getch()):
            if key == curses.KEY_RESIZE:
                logging.debug(f"Key pressed: {key}, {chr(key)}")
                if time() - current_time > .1:
                    handle_resize()
                    current_time = time()
                key = None
            elif key == ord('q'):
                exit_labelling()
            else:
                logging.debug(f"Key pressed: {key}, {chr(key)}")
                curses.ungetch(key)
                while stdscr.getch() in [key, curses.KEY_RESIZE]: #handles multiple keypresses (holding down a key)
                    break
        return key
    
    # we want to wait for a specific set of keys
    keys += [ord('q')]
    current_time = time()
    logging.debug(f"in await_keypress: specific keys {keys}")
    while (key:=stdscr.getch()) not in keys:
        if key == curses.KEY_RESIZE:
            logging.debug(f"Key pressed: {key}, {chr(key)}")
            if time() - current_time > .1:
                handle_resize()
                current_time = time()
    if key == ord('q'):
        exit_labelling()
        # handles multiple keypresses (holding down a key)
    while stdscr.getch() in [key, curses.KEY_RESIZE]:
        pass
    return key