import os
import sys
from lib.arg_parser import main_parser, \
    runserver_parser

from application import create_app, run_app

import config


def main(args):
    """This function is starting and configuring the hole sanic application"""
    args, extra = args

    if args.command == 'runserver':
        if 'help' in extra:
            runserver_parser.print_help()
            return

        args = runserver_parser.parse_args(extra)
        app = create_app(config=config)
        run_app(
            app=app,
            host=args.H or 'localhost',
            port=args.p or 8000,
            workers=args.w or 1,
        )


if __name__ == '__main__':
    os.environ.setdefault('SANIC_APP_NAME', config.SANIC_APP_NAME)
    arguments = main_parser.parse_known_args(sys.argv)
    main(arguments)

