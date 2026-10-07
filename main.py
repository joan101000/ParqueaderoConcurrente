import customtkinter as ctk

from multiprocessing import freeze_support

from interfaz import InterfazParqueadero


def main():

    ctk.set_appearance_mode(
        "dark"
    )

    app = InterfazParqueadero()

    app.mainloop()


if __name__ == "__main__":

    freeze_support()

    main()