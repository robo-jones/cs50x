/**
 * Implements a dictionary's functionality.
 */

#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>

#include "dictionary.h"

//file-scoped 'size' variable: incremented by load() for each word loaded and then returned by size(); set back to zero by unload()
//in order to satisfy the specification for size() (returns 0 if no dictionary loaded)
static unsigned int dictionary_size = 0;

//trie node structure, used for the dictionary (as suggested in the lecture)
typedef struct dict_node
{
    bool is_word_end;
    struct dict_node *characters[27];
} dict_node;

//prototypes
void add_to_dict(dict_node *node, char *word, const int length, const int chars_left);
int hash(char character);
dict_node* new_dict_node(void);
void free_node(dict_node *node);
bool search_dict(dict_node *node, const char *word, const int length, const int chars_left);

//size of the trie node; calculated once here for optimization purposes
const int node_size = sizeof(dict_node);

//the actual dictionary
dict_node *dict_root;

/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char *word)
{
    const int length = strlen(word);
    return search_dict(dict_root, word, length, length);
}

/**
 * Loads dictionary into memory. Returns true if successful else false.
 */
bool load(const char *dictionary)
{
    FILE *dict_file = fopen(dictionary, "r");
    if (dict_file == NULL)
    {
        return false;
    }
    //allocate memory for the top-level dict_node and initialize it
    dict_root = new_dict_node();

    //temporary word storage (leaving room for the terminating '\0')
    char word[LENGTH + 1];

    //read every word in the file, storing it in word, then add it to the trie and update dictionary_size
    for (int x = fscanf(dict_file, "%s", word); x != EOF; x = fscanf(dict_file, "%s", word))
    {
        int word_length = strlen(word);
        add_to_dict(dict_root, word, word_length, word_length);
        dictionary_size++;
    }

    fclose(dict_file);
    return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    return dictionary_size;
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    dictionary_size = 0;
    free_node(dict_root);
    return true;
}

/**
 * Adds a word to the dictionary
 */
void add_to_dict(dict_node *node, char *word, const int length, const int chars_left)
{
    //if this is the end of the word, update the node to reflect that, then return
    if (chars_left == 0)
    {
        node->is_word_end = true;
        return;
    }

    int hashed_char = hash(word[length - chars_left]);

    //if there is already a pointer for this character, then continue through the trie
    if (node->characters[hashed_char] != NULL)
    {
        add_to_dict(node->characters[hashed_char], word, length, chars_left - 1);
    }

    //otherwise, we need to create a new trie node and point this character at it
    else
    {
        dict_node *new_node = new_dict_node();
        node->characters[hashed_char] = new_node;
        add_to_dict(node->characters[hashed_char], word, length, chars_left - 1);
    }
}

/**
 * Simple hashing function that takes an ASCII character and converts it to an integer (0-25 = a-z, 26 = ')
 */
int hash(char character)
{
    if (character == 39) //apostrophe
    {
        return 26;
    }
    else
    {
        return tolower(character) - 97;
    }
}

/**
 * Dynamically allocate memory for a new dict_node, initialize it, and return a pointer to it
 */
dict_node* new_dict_node(void)
{
    dict_node *new_node = malloc(node_size);

    //initialize all the values in the node to their appropriate defaults to overwrite whatever garbage data was on the heap in this location
    for (int i = 0; i < 27; i++)
    {
        new_node->characters[i] = NULL;
    }
    new_node->is_word_end = false;

    return new_node;
}

/**
 * Free all memory used by a given dict_node
 */
void free_node(dict_node *node)
{
    //free all children of this node
    for (int i = 0; i < 27; i++)
    {
        //if there is a pointer here, free all memory used by that node's children
        if (node->characters[i] != NULL)
        {
            free_node(node->characters[i]);
        }
    }

    //now that we have freed all the children, we can free the node itself
    free(node);
}

/**
 * Recursively earches the dictionary for a given word, returning true if the word is in the dictionary, false otherwise
 */
bool search_dict(dict_node *node, const char *word, const int length, const int chars_left)
{
    //if this is the last character in the word, check if this node is a valid word ending and return true if it is, false otherwise
    if (chars_left == 0)
    {
        return node->is_word_end;
    }
    else
    {
        int hashed_char = hash(word[length - chars_left]);
        if (node->characters[hashed_char] == NULL)
        {
            return false;
        }
        else
        {
            return search_dict(node->characters[hashed_char], word, length, chars_left - 1);
        }
    }
}