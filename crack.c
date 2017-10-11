#include <stdio.h>
#include <cs50.h>
#include <string.h>
#define _XOPEN_SOURCE
#include <unistd.h>
#include <crypt.h>

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("Usage: crack <hashed password>\n");
        return 1;
    }

    char salt[2];
    salt[0] = argv[1][0];
    salt[1] = argv[1][1];

    char testKey[5];
    testKey[1] = '\0';

    //check single-character passwords
    for (int i = 65; i <= 122; i++)
    {
        //skip the characters between upper and lowercase letters
        if (i == 91)
        {
            i = 97;
        }

        testKey[0] = i;

        if (strcmp(crypt(testKey, salt), argv[1]) == 0)
        {
            printf("%s\n", testKey);
            return 0;
        }
    }

    //check two-character passwords
    testKey[2] = '\0';
    for (int i = 65; i <= 122; i++)
    {
        //skip the characters between upper and lowercase letters
        if (i == 91)
        {
            i = 97;
        }

        testKey[0] = i;
        for (int j = 65; j <= 122; j++)
        {
            //skip the characters between upper and lowercase letters
            if (j == 91)
            {
                j = 97;
            }

            testKey[1] = j;

            if (strcmp(crypt(testKey, salt), argv[1]) == 0)
            {
                printf("%s\n", testKey);
                return 0;
            }
        }
    }

    //check three-character passwords
    testKey[3] = '\0';
    for (int i = 65; i <= 122; i++)
    {
        //skip the characters between upper and lowercase letters
        if (i == 91)
        {
            i = 97;
        }

        testKey[0] = i;
        for (int j = 65; j <= 122; j++)
        {
            //skip the characters between upper and lowercase letters
            if (j == 91)
            {
                j = 97;
            }

            testKey[1] = j;
            for (int k = 65; k <= 122; k++)
            {
                //skip the characters between upper and lowercase letters
                if (k == 91)
                {
                    k = 97;
                }

                testKey[2] = k;

                if (strcmp(crypt(testKey, salt), argv[1]) == 0)
                {
                    printf("%s\n", testKey);
                    return 0;
                }
            }
        }
    }

    //check four-character passwords
    testKey[4] = '\0';
    for (int i = 65; i <= 122; i++)
    {
        //skip the characters between upper and lowercase letters
        if (i == 91)
        {
            i = 97;
        }

        testKey[0] = i;
        for (int j = 65; j <= 122; j++)
        {
            //skip the characters between upper and lowercase letters
            if (j == 91)
            {
                j = 97;
            }

            testKey[1] = j;
            for (int k = 65; k <= 122; k++)
            {
                //skip the characters between upper and lowercase letters
                if (k == 91)
                {
                    k = 97;
                }

                testKey[2] = k;
                for (int l = 65; l <= 122; l++)
                {
                    //skip the characters between upper and lowercase letters
                    if (l == 91)
                    {
                        l = 97;
                    }

                    testKey[3] = l;

                    if (strcmp(crypt(testKey, salt), argv[1]) == 0)
                    {
                        printf("%s\n", testKey);
                        return 0;
                    }
                }
            }
        }
    }
}