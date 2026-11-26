"""Run the menus with ``python -m ui`` (from the FinalProject/src folder).

A temporary front door: it lets us try the new menus without touching
main.py, which Jason's level branch is still editing.
"""


from ui.game import Game

if __name__ == "__main__":  # pragma: no cover
    Game().run()  
