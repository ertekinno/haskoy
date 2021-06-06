from fontTools.ttLib import TTFont
import sys


def main():
    filepath = sys.argv[1]
    tt = TTFont(filepath)
    tt["head"].macStyle |= 1 << 1  # Set Italic bit
    tt["OS/2"].fsSelection &= ~(1 << 5)  # Clear Bold bit
    tt["OS/2"].fsSelection &= ~(1 << 6)  # Clear Regular bit
    tt["OS/2"].fsSelection |= 1 << 0  # Set Italic bit
    tt.save(filepath)
    print(f"Set Italic bit of {filepath}")


if __name__ == "__main__":
    main()
