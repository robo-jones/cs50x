/**
 * Searches a file and itentifies, then saves any .jpg images
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/**
 * function declarations
 */
bool is_jpg_start(uint8_t *block);
FILE* get_new_outfile(int file_number);

int main(int argc, char *argv[])
{
    // verify input
    if (argc != 2)
    {
        fprintf(stderr, "usage: recover filename\n");
        return 1;
    }

    // attempt to open the input file for reading
    FILE *infile = fopen(argv[1], "r");
    if (infile == NULL)
    {
        fprintf(stderr, "error opening file \"%s\".\nPlease check the filename and try again.\n", argv[1]);
        return 2;
    }

    // create a temporary storage space for a single FAT block
    uint8_t *block = malloc(512);

    // track the number of files that have been created, for naming purposes
    int files_written = 0;

    // track the number of bytes read by fread(); if the number is not 512, then we have reached the end of the file
    int bytes_read = 0;

    // read the first block of the file
    bytes_read = fread(block, 1, 512, infile);

    // loop through the entire file
    while (bytes_read == 512)
    {
        // check if this block contains the start of a .jpg file, and if it does, start writing the blocks to a new file
        if (is_jpg_start(block))
        {
            // create and open a new file to write the blocks to
            FILE *outfile = get_new_outfile(files_written);
            if (outfile == NULL)
            {
                fprintf(stderr, "error creating file %0*i.jpg", 3, files_written);
                return 2;
            }
            files_written++;

            // write blocks to the file until the beginning of another .jpg or the end of the file is reached
            do
            {
                fwrite(block, 512, 1, outfile);
                bytes_read = fread(block, 1, 512, infile);
            } while (!is_jpg_start(block) && bytes_read == 512);
            fclose(outfile);
        }
        else
        {
            // if the block did not contain the start of a .jpg, read the next block and start again
            bytes_read = fread(block, 1, 512, infile);
        }
    }

    // free up memory and close infile
    free(block);
    fclose(infile);
    return 0;
}

/**
 * Helper function that examines through the first four bytes of a block to determine if they are the start of a .jpg file,
 * i.e. the first 4 bytes are 0xff, 0xd8, 0xff, and 0xe0-0xef
 */

bool is_jpg_start(uint8_t *block)
{
    if (block[0] == 0xff)
    {
        if (block[1] == 0xd8)
        {
            if (block[2] == 0xff)
            {
                if (0xe0 <= block[3] && block[3] <= 0xef)
                {
                    return true;
                }
            }
        }
    }

    return false;
}

/**
 * Helper function to create a new, 3-digit filename (e.g. "002.jpg"), and then open a new file with that filename, returning a
 * pointer to that file.
 */

FILE* get_new_outfile(int file_number)
{
    char filename[7];
    sprintf(filename, "%0*i.jpg", 3, file_number);
    return fopen(filename, "w");
}