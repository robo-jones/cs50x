/**
 * Copies a BMP piece by piece, just because.
 */

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./copy factor infile outfile\n");
        return 1;
    }

    //parse n and make sure it is an integer value from 1 to 100
    int n = atoi(argv[1]);
    if (n < 1 || n > 100)
    {
        fprintf(stderr, "Factor must be an integer value from 1 to 100\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 1;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 1;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 1;
    }

    // create new headers for the resized image file
    BITMAPFILEHEADER bf_new = bf;
    BITMAPINFOHEADER bi_new = bi;
    bi_new.biHeight *= n;
    bi_new.biWidth *= n;
    // determine padding for new file
    int padding_new = (4 - (bi_new.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    // calculate the new row size (in bytes) and use it to determine the new image size (in bytes)
    bi_new.biSizeImage = ((bi_new.biWidth * sizeof(RGBTRIPLE)) + padding_new) * abs(bi_new.biHeight);
    // calculate the new file size
    bf_new.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + bi_new.biSizeImage;

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf_new, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi_new, sizeof(BITMAPINFOHEADER), 1, outptr);

    // determine padding input file
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // create a temporary array of RGBTRIPLEs to store the entire line to be written
    RGBTRIPLE *new_line = malloc(sizeof(RGBTRIPLE) * bi_new.biWidth);

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        // iterate over pixels in scanline
        for (int j = 0; j < bi.biWidth; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

            // write RGB triple to new_line
            for (int k = 0; k < n; k++)
            {
                new_line[(j * n) + k] = triple;
            }
        }

        // write new_line and any necessary padding to outfile n times
        for (int j = 0; j < n; j++)
        {
            fwrite(new_line, sizeof(RGBTRIPLE), bi_new.biWidth, outptr);

            // add any padding to outfile
            for (int k = 0; k < padding_new; k++)
            {
                fputc(0x00, outptr);
            }
        }

        // skip over infile padding, if any
        fseek(inptr, padding, SEEK_CUR);
    }

    // free the new line storage
    free(new_line);

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
