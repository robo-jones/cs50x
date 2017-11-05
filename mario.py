

def main():
    height = get_int_input("Height: ")

    while isinstance(height, int) == False or height < 0 or height > 23:
        print("Height must be non-negative and no greater than 23.")
        height = get_int_input("Height: ")

    hashes = ""
    for i in (range(1, height + 1)):
        hashes += "#"
        print("{:>{height}}  {:{height}}".format(hashes, hashes, height=height))


# A bit of a dirty hack to type check the value received from input() that uses exception handling.
# Sure, I could have used the cs50 library, but where's the fun in that?
def get_int_input(prompt):
    while True:
        i = input(prompt)
        try:
            i = int(i)
            break
        except ValueError:
            print("Please enter an integer value")

    return i

if __name__ == "__main__":
    main()