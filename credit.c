#include <stdio.h>
#include <cs50.h>

int getDigit(long long number, int digit);
long long power(int base, int exponent);
bool hasValidChecksum(int digits[], int length);
int findLength(long long number);

int main(void) {
    long long cardNumber = get_long_long("Number: ");
    int length = findLength(cardNumber);
    int digits[length];

    for (int i = 0; i < length; i++) {
        //store digits in reverse order; makes things easier to reason about, at least for me
        digits[i] = getDigit(cardNumber, i);
    }

    switch (length) {
        case 13: {
            if (digits[12] == 4 && hasValidChecksum(digits, length)) {
                printf("VISA\n");
                return 0;
            } else {
                printf("INVALID\n");
                return 0;
            }
            break;
        }

        case 15: {
            if (digits[14] == 3 && (digits[13] == 4 || digits[13] == 7) && hasValidChecksum(digits, length)) {
                printf("AMEX\n");
                return 0;
            } else {
                printf("INVALID\n");
                return 0;
            }
            break;
        }

        case 16: {
            if (digits[15] == 4 && hasValidChecksum(digits, length)) {
                printf("VISA\n");
                return 0;
            } else if (digits[15] == 5 && digits[14] >= 1 && digits[14] <= 5 && hasValidChecksum(digits, length)) {
                printf("MASTERCARD\n");
                return 0;
            } else {
                printf("INVALID\n");
                return 0;
            }
            break;
        }

        default: {
            printf("INVALID\n");
            return 0;
        }
    }
}

int getDigit(long long number, int index) {
    int digit = index + 1;
    return (((number % power(10, digit)) - (number % power(10, digit - 1))) / power(10, (digit - 1)));
}

long long power(int base, int exponent) {
    long long result = 1;
    for (int i = 0; i < exponent; i++) {
        result = result * base;
    }
    return result;
}

bool hasValidChecksum(int digits[], int length) {
    int checksum = 0;
    //double every other digit, starting with the second-to-last
    for (int i = 1; i < length; i += 2) {
        checksum += (((2 * digits[i]) / 10) + ((2 * digits[i]) % 10));
    }
    //add every other digit, starting with the last
    for (int i = 0; i < length; i += 2) {
        checksum += digits[i];
    }

    if ((checksum % 10) == 0) {
        return true;
    } else {
        return false;
    }
}

int findLength(long long number) {
    int length = 1;
    while ((number % power(10, length)) != number) {
        length += 1;
    }

    return length;
}