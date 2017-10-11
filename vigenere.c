#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("Usage: vignere <key>\n");
        return 1;
    }

    string key = argv[1];
    int keyLength = strlen(argv[1]);
    for (int i = 0; i < keyLength; i++)
    {
        if (!isalpha(key[i]))
        {
            printf("Key may only contain letters\n");
            return 1;
        }
    }

    printf("plaintext: ");
    string plaintext = get_string();

    printf("ciphertext: ");
    for (int i = 0, j = 0, n = strlen(plaintext); i < n; i++)
    {
        //if the character in plaintext is a letter, then print out the ciphered letter, otherwise just print out the character
        if (isalpha(plaintext[i]))
        {
            int offset = toupper(key[j]) - 65;
            //check if the ciphered letter has "overflowed", and if so, wrap it back around
            if ((isupper(plaintext[i]) && !isupper(plaintext[i] + offset)) || (islower(plaintext[i]) && !islower(plaintext[i] + offset)))
            {
                printf("%c", plaintext[i] + offset - 26);
            }
            else
            {
                printf("%c", plaintext[i] + offset);
            }
            //advance to the next character in the key, wrapping around to the first if the end is reached
            j += 1;
            if (j == keyLength) {
                j = 0;
            }
        }
        else
        {
            printf("%c", plaintext[i]);
        }
    }

    printf("\n");
}