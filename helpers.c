/**
 * helpers.c
 *
 * Helper functions for Problem Set 3.
 */

#include <cs50.h>

#include "helpers.h"

#define MAX_VALUE 65536 //based on the problem specification, values[] contains unsigned integers that are less than this value
bool binarySearch(int value, int values[], int minIndex, int maxIndex);

/**
 * Returns true if value is in array of n values, else false.
 */
bool search(int value, int values[], int n)
{
    if (n < 0)
    {
        return false;
    }
    else
    {
        return binarySearch(value, values, 0, (n - 1));
    }
}

bool binarySearch(int value, int values[], int minIndex, int maxIndex)
{
    int halfwayIndex = (minIndex + maxIndex) / 2; //look in the middle of the range to be searched
    /**
     * If there are only two elements left to be searched, halfwayIndex will end up being equal to minIndex, thanks to integer division.
     * If the first of those two elements does not happen to be value, the program will get caught in an infinite recursion, since it will not change minIndex on the next call.
     * Therefore, if halfwayIndex == minIndex, we must check the two remaining values manually
     */
    if (halfwayIndex == minIndex)
    {
        if (value == values[minIndex] || value == values[maxIndex])
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    if (value == values[halfwayIndex]) //we found the value
    {
        return true;
    }
    else if (value < values[halfwayIndex])
    {
        //if the value is less than the number we are looking at, search the left half of the remaining array
        return binarySearch(value, values, minIndex, halfwayIndex);
    }
    else
    {
        //if the value is greater than the number we are looking at, search the right half of the remaining array
        return binarySearch(value, values, halfwayIndex, maxIndex);
    }
}

/**
 * Sorts array of n values.
 */
void sort(int values[], int n)
{
    int valueCounts[MAX_VALUE] = {0}; //initializes all values in the array to 0, in order to prevent unexpected, hilarious segfaults

    //iterate through values[] and count the number of times that each value occurs
    for (int i = 0; i < n; i++)
    {
        valueCounts[values[i]]++;
    }

    /**
     * Iterate through valueCounts[]. Each time a nonzero number is encountered (i.e. that particular value of i was found in values[]), it is placed back into values[].
     * j is used to store the current position in values[], so it is incremented each time we place a new value into values.
     * Decrementing valueCounts[i] and placing the whole of the logic into a while loop allows handling of duplicate values.
     */
    for (int i = 0, j = 0; i < MAX_VALUE; i++)
    {
        while (valueCounts[i] > 0)
        {
            values[j] = i;
            valueCounts[i]--;
            j++;
        }
    }

    return;
}
