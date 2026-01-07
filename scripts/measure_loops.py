#!/usr/bin/env python3

# Assumption Resetter
# Implements Constitution §6.4 (Assumption Reset Rule)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def print_banner() -> None:
    print(f"{RED}╔════════════════════════════════════════════════════════════╗{NC}")
    print(f"{RED}║              COMPILER LOOP DETECTED (STOP)                 ║{NC}")
    print(f"{RED}╚════════════════════════════════════════════════════════════╝{NC}")
    print(f"\n{YELLOW}You have failed to fix a compile/test error more than once.{NC}")
    print(f"{YELLOW}Per Constitution §6.4, you MUST perform an Assumption Reset.{NC}\n")


def main() -> None:
    print_banner()

    print(f"{BLUE}Step 1: Consult the Playbook{NC}")
    print("Read: docs/playbooks/compiler-loops.md")
    print("Does your error match a known pattern? (Haskell/Elm specific)\n")

    print(f"{BLUE}Step 2: Explicitly State the Wrong Assumption{NC}")
    print("Examples:")
    print(" - 'I assumed I could cast String to Text implicitly.'")
    print(" - 'I assumed I could use side effects in this pure function.'")
    print(" - 'I assumed this library worked like the Python equivalent.'\n")

    print(f"{BLUE}Step 3: The Reset{NC}")
    print("1. Revert the last attempt.")
    print("2. Write the fix using the CORRECT model from the playbook.")
    print("3. If the playbook has no entry, create a new one after solving this.")

    print(f"\n{GREEN}Verification:{NC}")
    print("Does the code compile? If not, do NOT retry blindly.")


if __name__ == "__main__":
    main()
