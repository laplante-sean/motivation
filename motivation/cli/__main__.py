'''
Motivation CLI
'''
import os
import sys
import asyncio
import logging
import argparse
import traceback

from motivation.ble import BLEScanner, BLEClient
from motivation.power import RawPowerTracker, AveragePowerTracker


def clear_screen():
    '''
    Clear the sceen (os independent)
    '''
    os.system("cls" if os.name == 'nt' else 'clear')


def select_device(scanner):
    '''
    Allow the user to select the device
    '''
    clear_screen()

    while 1:
        print("Looking for compatible devices...")

        devices = scanner.scan()

        print("\nChoose your device:")
        print("\t0. Rescan")
        for idx, d in enumerate(devices):
            choice = idx + 1
            print(f"\t{choice}. {d.name}")

        try:
            choice = input("\nWhich device? ")
        except KeyboardInterrupt:
            print("Exit...")
            sys.exit(0)

        try:
            choice = int(choice)

            if choice > len(devices) or choice < 0:
                raise ValueError("no")
        except ValueError:
            print("Invalid. You're bad at computers.")
            sys.exit(1)

        if choice == 0:
            clear_screen()
            continue
        break

    device = devices[choice - 1]
    print(f"Choice: {device.name}")
    return device


def main_cli():
    '''
    Entry Point
    '''
    parser = argparse.ArgumentParser("Fit Gaming Motivation!", description="Keeps you motivated while gaming or you can't game.")
    parser.add_argument("-t", "--timeout", action="store", type=int, help="Connection timeout", required=False, default=10)
    parser.add_argument("-w", "--write-out", action="store", help="Record raw data in this directory", default="data")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging to stdout")
    parser.add_argument("-v", "--verbose", action="store_true", help="More output. This will include Bleak library output.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-p", "--power-threshold", action="store", type=int, help="Under this value you can't play games")
    group.add_argument("-a", "--average-power", action="store", type=int, help="Under this average power or you can't play")
    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    log_stdout_handler = logging.StreamHandler(sys.stdout)
    log_stdout_handler.setLevel(level)
    root_logger.addHandler(log_stdout_handler)

    # Validate some arguments
    if not os.path.isdir(args.write_out):
        try:
            os.mkdir(args.write_out)
        except OSError as e:
            print(f"Failed to create directory for output data: {e}")
            sys.exit(1)

    tracker = None

    if args.power_threshold:
        tracker = RawPowerTracker(args.power_threshold)
    elif args.average_power:
        tracker = AveragePowerTracker(args.average_power)
    else:
        print("One of -a/--average-power or -p/--power-threshold are required.")
        sys.exit(1)

    # TODO: Create a recorder object. Recorder object will create datetime stamped files for this activity

    scanner = BLEScanner(debug=args.debug)

    # Get the user's device selection
    device = select_device(scanner)

    # Run the ble code
    client = BLEClient(device.metadata.get("uuids")[0], device.address, tracker, args.timeout, args.debug)
    client.run()
    '''
    address = device.address
    success = loop.run_until_complete(run_client(tracker, address, loop, timeout=args.timeout))
    if not success:
        sys.exit(1)
    '''


if __name__ == "__main__":
    try:
        main_cli()
    except Exception as e:
        # Catch any unhandled exceptions and create a bug report file
        bugreport = os.path.join(os.path.expanduser("~"), "motivation_bugreport.txt")

        print(f"Exception: {e}")
        print(f"See {bugreport} for more error information.")

        with open(bugreport, 'w') as fh:
            traceback.print_exc(file=fh)

        sys.exit(1)

    sys.exit(0)
