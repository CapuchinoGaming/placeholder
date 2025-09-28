import platform, subprocess

# This function takes an audio file, then plays it
def play_audio(filename):
    print("> Running try_platform_player()")
    try:
        system = platform.system()
        if system == "Darwin":     # macOS
            return subprocess.call(["afplay", filename]) == 0
        elif system == "Windows":
            import winsound
            print("> Playing sound")
            winsound.PlaySound(filename, winsound.SND_FILENAME)
            print("> Sound was played")
            return True
        else:                      # Linux/*nix
            # Try common CLI players in order
            for player in (["ffplay", "-nodisp", "-autoexit", filename],
                        ["aplay", filename],
                        ["paplay", filename]):
                try:
                    if subprocess.call(player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        return True
                except FileNotFoundError:
                    continue
        return False
    except Exception:
        return False