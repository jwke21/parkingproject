from program import Loader, Program


def main():
    try:
        program = Loader.launch_program()
        program.program_loop()
        Loader.save_program(program)
    except KeyboardInterrupt:
        Loader.save_program(program)


if __name__ == "__main__":
    main()
