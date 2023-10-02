from os import getenv
import argparse
import re
from typing import List
import cattr
import pathlib
import sys

from mytpu.api import MyTPU
import json

from mytpu.models import Service


def get_args():
    parser = argparse.ArgumentParser(description="Download usage data from mytpu.org")
    parser.add_argument(
        "--username",
        type=str,
        help="MyTPU Username (default: MYTPU_USERNAME environment variable)",
        default=getenv("MYTPU_USERNAME"),
    )
    parser.add_argument(
        "--password",
        type=str,
        help="MyTPU password (default: MYTPU_PASSWORD environment variable)",
        default=getenv("MYTPU_PASSWORD"),
    )
    # TODO: hook this up
    # parser.add_argument(
    #     "--config",
    #     type=pathlib.Path,
    #     help="Path to config file with user/password",
    # )

    parser.add_argument(
        "--meters",
        type=str,
        help="comma separated list of meter type or id (e.g. all,power,water,11110123)",
        default='all',
    )

    subparsers = parser.add_subparsers(dest="command", help="command help")

    # create parsers for subcommands
    sub = {}

    sub["list-meters"] = subparsers.add_parser(
        "list-meters", help="List the meters on the account"
    )

    sub["account-summary"] = subparsers.add_parser("account-summary", help="Get customer account summary")
    sub["usage"] = subparsers.add_parser("usage", help="Get usage")

    # Parse the args
    args = parser.parse_args()

    if not args.username or not args.password:
        parser.print_help()
        sys.exit(1)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    meters = set()
    for meter in args.meters.lower().split(','):
        if meter == 'all':
            meters = {'P', 'W'}
            break
        elif meter == 'power':
            meters.add('P')
        elif meter == 'water':
            meters.add('W')
        elif re.match(r'^\d+$', meter):
            meters.add(meter)
        else:
            print(f"Invalid meter: {args.meters}", file=sys.stderr)
            sys.exit(1)
    args.meters = meters

    return args


def list_meters(tpu: MyTPU, args: argparse.Namespace):
    """
    List all requested meters (services) on the account.
    """
    services = tpu.customer().accountSummaryType.get_meters(args.meters, True)
    for service in services:
        print(f"{service.friendly_meter_type}: {service.meterNumber}")


def main():

    args = get_args()
    # Connect to the service and load the customer info (which is needed for other commands)
    tpu = MyTPU(args.username, args.password)
    customer = tpu.customer()

    match args.command:
        case "account-summary":
            print(json.dumps(tpu.customer().unstructure(), sort_keys=True, indent=True))
        case "list-meters":
            list_meters(tpu, args)
        case "usage":
            meters = tpu.customer().accountSummaryType.get_meters(args.meters, True)
            meter_usage = {}
            # usage = tpu.usage(
            #     context=customer.accountContext,
            #     service=customer.accountSummaryType.servicesForGraph[1],

            #     # dates are always  12:00 to 11:59

            #     from_date="2022-09-01 12:00",
            #     to_date="2022-09-02 12:59",
            #     hourly=False, 
            # )
            # print(json.dumps(usage, sort_keys=True, indent=2))
            for meter in meters:
                usage = tpu.usage(
                    context=customer.accountContext,
                    service=meter,
                    # No actual difference in results with the different hours
                    # from_date="2022-09-01 10:59",  # 15-min interval?
                    from_date="2022-09-01 12:00",  # hourly
                    to_date="2022-09-01 11:59",
                    hourly=True, 
                )
                # print(json.dumps(usage, sort_keys=True, indent=2))
                if 'history' not in usage:
                    usage = {'unexpectedResult': usage}
                usage['meterNumber'] = meter.meterNumber
                usage['meterType'] = meter.friendly_meter_type
                meter_usage[meter.meterNumber] = usage
            print(json.dumps(meter_usage, sort_keys=True, indent=2))

    # account = tpu.get_all_accounts()[0]
    # print(json.dumps(customer.unstructure(), sort_keys=True, indent=4))

    # then user()
    # then usage()
