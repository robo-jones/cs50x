

def main():
    # Constants that define the properties of various credit card issuers' numbers
    visaLengths = [13, 16]
    visaPrefixes = ["4"]
    amexLengths = [15]
    amexPrefixes = ["34", "37"]
    mastercardLengths = [16]
    mastercardPrefixes = ["51", "52", "53", "54", "55"]

    ccNum = get_int_input_as_str("Number: ")

    if is_valid_luhn_checksum(ccNum):
        if len(ccNum) in visaLengths and ccNum[0] in visaPrefixes:
            print("VISA")
        elif len(ccNum) in amexLengths and ccNum[0:2] in amexPrefixes:
            print("AMEX")
        elif len(ccNum) in mastercardLengths and ccNum[0:2] in mastercardPrefixes:
            print("MASTERCARD")
        else:
            print("INVALID")
    else:
        print("INVALID")


# A bit of a dirty hack to type check the value received from input() that uses exception handling.
# Sure, I could have used the cs50 library, but where's the fun in that?
def get_int_input_as_str(prompt):
    while True:
        i = input(prompt)
        try:
            int(i)
            break
        except ValueError:
            print("Please enter an integer value")

    return i

def is_valid_luhn_checksum(ccNumString):
    checksum = 0
    index = 1 # Luhn algorithm is 1-indexed

    # iterate over the characters in the credit card number string, then cast them to ints to calculate the Luhn checksum
    for char in reversed(ccNumString):
        i = int(char)
        if index % 2 == 0:
            onesDigit = (i * 2) % 10
            tensDigit = (i * 2) // 10
            checksum += (onesDigit + tensDigit)
        else:
            checksum += i
        index += 1

    return (checksum % 10 == 0) # evaluates to True if the last digit is a 0, False otherwise

if __name__ == "__main__":
    main()