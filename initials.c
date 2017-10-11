#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    string name = get_string();
    bool isNextWord = true; //tracks whether the below loop has encountered the end of a word (i.e. a space)
    for (int i = 0, n = strlen(name); i < n; i++)
    {
        if (name[i] != ' ') //there is a non-space character
        {
            //if the loop has not yet encountered a non-space character in this word, print it out in uppercase, then set isNextWord to false to tell the loop to skip any firther characters in this word
            if (isNextWord)
            {
                printf("%c", toupper(name[i]));
                isNextWord = false;
            }
        }
        else
        {
            //if there is a space character, then the previous word has ended (or hasn't started yet, in the case of leading spaces), so set isNextWord to true
            isNextWord = true;
        }
    }
    printf("\n");
}