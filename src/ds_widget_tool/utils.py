import sys


def feedback(message):
    print()
    print(message)
    print()

def error_exit(message, exit_code = 1):
    feedback(f'❌ ERROR: {message}\n\nExiting with code {exit_code}.\n')
    sys.exit(exit_code)