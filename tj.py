import os
import subprocess
import time
import argparse
import pathlib
from colorama import init, Fore

def clean(PATH_TO_TESTS: pathlib.Path):
    os.chdir(PATH_TO_TESTS)
    os.remove("res*")

def make(NALOGA: int, PATH_TO_TESTS: str, time_it: bool = True):
    try:
        subprocess.run(["javac", f"Naloga{NALOGA}.java"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        exit(e.returncode)

    init(autoreset=True)
    for t in range(1, 100):
        print(f"test{t:02d}: ", end="")
        try:
            if time_it: timed = time.perf_counter()
            subprocess.run(["java", f"Naloga{NALOGA}", os.path.join(PATH_TO_TESTS, f"vhod{t:02d}.txt"), os.path.join(PATH_TO_TESTS, f"izhod{t:02d}.txt")], check=True)
            if time_it: timed = time.perf_counter() - timed
            print(Fore.GREEN + "OK", end="" if time_it else "\n")
            # print(f", time: {round(timed, 3)}" if time_it else "")
            if time_it:
                print(", time: ", end="")
                if timed > 2: print(Fore.RED + f"{round(timed, 3)} TIMEOUT")
                else: print(round(timed, 3))

        except subprocess.CalledProcessError as e:
            print(Fore.RED + "Error: " + e.stderr)

def compare(NALOGA: int, PATH_TO_TESTS: str, time_it: bool = True):
    try:
        subprocess.run(["javac", f"Naloga{NALOGA}.java"], capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode("ascii"))
        exit(e.returncode)
    
    init(autoreset=True)
    pravilno = 0

    for t in range(1, 100):
        print(f"test{t:02d}: ", end="")
        try:
            if time_it: timed = time.perf_counter()
            subprocess.run(["java", f"Naloga{NALOGA}", os.path.join(PATH_TO_TESTS, f"vhod{t:02d}.txt"), os.path.join(PATH_TO_TESTS, f"res{t:02d}.txt")], timeout=2, check=True)
            if time_it: timed = time.perf_counter() - timed

            res: subprocess.CompletedProcess = subprocess.run(["diff", os.path.join(PATH_TO_TESTS, f"res{t:02d}.txt"), os.path.join(PATH_TO_TESTS, f"izhod{t:02d}.txt")], stdout=subprocess.DEVNULL)
            if res.returncode == 0:
                pravilno += 1
                print(Fore.GREEN + "[+]", end="")
            else:
                print(Fore.RED + "[-]", end="")
            print(f" time: {round(timed, 3)}" if time_it else "")

        except subprocess.TimeoutExpired:
            print(Fore.MAGENTA + "[*]" + " TIMEOUT")
        except subprocess.CalledProcessError:
            print(Fore.YELLOW + "[*]")

    print(f"Pravilno: {pravilno}/99")

def main():

    available_actions = ("compare", "make", "clean")

    parser = argparse.ArgumentParser(description="Avtomatsko testiranje za 1. seminarsko nalogo pri aps1")

    # parser.add_argument("-n", "--naloga", help="Katera naloga se testira. Npr. (naloga=) 1 --> testiraj Naloga1.java", nargs='+', choices=["1", "2", "3", "4", "5"], required=True)
    parser.add_argument("naloga", help="Katera naloga se testira. Npr. (naloga=) 1 --> testiraj Naloga1.java", choices=["1", "2", "3", "4", "5"])
    parser.add_argument("-a", "--action", help="Katera operacija se izvede. Privzeto je compare", choices=available_actions, default="compare")
    parser.add_argument("--list-actions", help="Izpiše možne operacije", action="store_true", dest="list_actions")
    parser.add_argument("--path", help="Pot do direktorija z datoteko NalogaX.java. Privzeto je ./<naloga>/", type=pathlib.Path)
    parser.add_argument("--testi", help="Pot do direktorija s testi. Privzeto je ./<path>/testi/", type=pathlib.Path)
    parser.add_argument("-t", "--time", help="Izmeri koliko časa potrebuje program", action="store_true", default=False)
    args = parser.parse_args()
    
    if args.list_actions:
        for action in available_actions: print(action)
        exit(0)

    if args.path is None: args.path = args.naloga
    try:
        os.chdir(args.path)
    except FileNotFoundError as e:
        print(e)
        exit(e.errno)
    
    if args.testi is None: args.testi = os.path.join(args.path, "testi")
    
    if args.action == "compare": compare(args.naloga, args.testi, time_it=args.time)
    elif args.action == "make": make(args.naloga, args.testi, time_it=args.time)
    elif args.action == "clean": clean(args.testi)

if __name__ == "__main__":
    main()