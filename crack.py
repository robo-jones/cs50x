# This implementation is less efficient than it could be, given how constrained the specifications are. However, it is significantly
# more generalized: by editing the two global constants, a much wider variety of passwords can be cracked.

import sys
import crypt

VALID_PASSWORD_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAX_PASSWORD_LENGTH = 4


def main():
    # check for correct number of command line arguments
    if len(sys.argv) != 2:
        print("usage: crack hashed_password")
        exit(1)

    target = sys.argv[1]
    salt = target[0:2] # crypt stores the salt as the first two characters in the hash

    for i in range(MAX_PASSWORD_LENGTH):
        passwords = generate_possible_passwords(VALID_PASSWORD_CHARACTERS, i)
        for password in passwords:
            if crypt.crypt(password, salt) == target:
                print(password)
                exit(0)

    exit(2)


# Recursize function that generates a list of all possible passwords of a given length. This has the potential to use an extrmeely
# high amount of memory when given a long length, but for the short passwords called for in the specifications, it is fine. This
# approach is used in the interest of making the code more readable and understandable.
def generate_possible_passwords(passwords, length):
    if length == 0:
        return passwords
    else:
        newPasswords = []
        for password in passwords:
            for char in VALID_PASSWORD_CHARACTERS:
                newPasswords.append(str(password + char))
        return generate_possible_passwords(newPasswords, length - 1)


if __name__ == "__main__":
    main()