import argparse


runserver_parser = argparse.ArgumentParser(description='Runserver options', add_help=True)
runserver_parser.add_argument('-H', type=str, help='Specify the host to run the server')
runserver_parser.add_argument('-p', type=int, help='Specify the port to run the server')
runserver_parser.add_argument('-w', type=int, help='Specify the number of workers to use')


main_parser = argparse.ArgumentParser(description='Manage.py deployment tool')
main_parser.add_argument('file', type=str, help='Executive file')
main_parser.add_argument('command', choices=[
                                'runserver',
                            ],
                         type=str, help='Command to execute')

