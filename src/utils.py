import sys

FEEDBACK_MODE = None

def feedback_mode(mode):
    global FEEDBACK_MODE
    if FEEDBACK_MODE != mode:
        print()
        FEEDBACK_MODE = mode

def success_feedback(message):
    feedback_mode('success')
    print(f"✅ {message}")


def info_feedback(message):
    feedback_mode('info')
    print(f"ⓘ {message}")

def error_feedback(message):
    feedback_mode('error')
    print(f"❌ ERROR: {message}")


def error_exit(message, exit_code = 1):
    error_feedback(f'{message}\n\nExiting with code {exit_code}.\n')
    sys.exit(exit_code)