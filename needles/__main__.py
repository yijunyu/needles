needles command line tool (enable python -m needles syntax)
"""

import sys

def main(): # needed for console script
    if __package__ == '':
        import os.path
        path = os.path.dirname(os.path.dirname(__file__))
        sys.path[0:0] = [path]
    import needles
    needles.main()

if __name__ == "__main__":
    main()
