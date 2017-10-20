/**
 * generate.c
 *
 * Generates pseudorandom numbers in [0,MAX), one per line.
 *
 * Usage: generate n [s]
 *
 * where n is number of pseudorandom numbers to print
 * and s is an optional seed
 */

#define _XOPEN_SOURCE

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// upper limit on range of integers that can be generated
#define LIMIT 65536

int main(int argc, string argv[])
{
    // check that the correct number of command-line arguments were passed into generate; if not, print a helpful error and terminate the program
    if (argc != 2 && argc != 3)
    {
        printf("Usage: ./generate n [s]\n");
        return 1;
    }

    // convert the first command-line argument (the number of random numbers to generate) from a string to an integer
    int n = atoi(argv[1]);

    // srand68 is an initialization functon that will seed drand48 to the provided seedval. here, we check if the user provided a seed value on the command-line (i.e. argc == 3), and if so, set the seed to that value. Otherwise, set the seed to the current UNIX time.
    if (argc == 3)
    {
        srand48((long) atoi(argv[2]));
    }
    else
    {
        srand48((long) time(NULL));
    }

    // print the requested number of pseudorandom numbers by multiplying the output of drand48 (a pseudorandom number between (0.0, 1.0]) by LIMIT, and then casting the result to an integer in order to round it off
    for (int i = 0; i < n; i++)
    {
        printf("%i\n", (int) (drand48() * LIMIT));
    }

    // success
    return 0;
}
