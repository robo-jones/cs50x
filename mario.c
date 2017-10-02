#include <stdio.h>
#include <cs50.h>

int main(void) {
    int height = get_int("Height: ");

    if (height < 0 || height > 23) {
        do {
            printf("Height must be non-negative and no greater than 23\n");
            height = get_int("Height: ");
        } while (height < 1 || height > 23);
    }

    for (int i = 0; i < height; i++) {
        for (int j = i; j < height - 1; j++) {
            printf(" ");
        }
        for (int j = 0; j < (i + 1); j++) {
            printf("#");
        }
        printf("  ");
        for (int j = 0; j < (i + 1); j++) {
            printf("#");
        }
        printf("\n");
    }
}