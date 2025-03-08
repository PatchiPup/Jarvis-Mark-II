exit = False

def exit_program():
    print("Exiting the program")
    global exit
    exit = True

def should_exit():
    return exit