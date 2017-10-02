#include <stdio.h>
#include <cs50.h>

int main(void) {
    printf("How many bottles of water do you consume when showering?\n");
    int minutes = get_int("Shower length (minutes): ");
    printf("Bottles consumed: %i\n", minutes * 12);
}