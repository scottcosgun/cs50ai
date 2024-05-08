import nltk
import sys
import os
import string
import math

FILE_MATCHES = 2
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dictionary = {}
    # Iterate through .txt files in directory
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            # Read contents of .txt file and save in dictionary
            with open(os.path.join(directory, file), 'r') as f:
                contents = f.read()
                dictionary[file] = contents
    
    return dictionary

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # Convert to lowercase and tokenize string
    tokenized = nltk.word_tokenize(document.lower())

    # Iterate through tokenized words
    for word in tokenized:
        # Filter out stopwords
        if word in nltk.corpus.stopwords.words("english"):
            tokenized.remove(word)
        # Filter out punctuation
        else:
            for char in word:
                if char in string.punctuation:
                    word.replace(char, '')
    
    return tokenized

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    appearances = dict()
    num_docs = len(documents)
    # Iterate through each document and take note of unique words in each one
    for document in documents.keys():
        words = set(documents[document])
        for word in words:
            if word not in appearances:
                appearances[word] = 1
            else:
                appearances[word] += 1
    
    # Compute IDFs and return dict
    return {k:(math.log(num_docs/appearances[k])) for k in appearances}

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {file:0 for file in files.keys()}
    # Iterate through files and calculate TF-IDFs for all words in query that appear in file
    for file in files.keys():
        for word in query:
            if word in files[file] and word in idfs:
                # Calculate tfidf and add to file's total
                tfidfs[file] += (files[file].count(word) * idfs[word])
    
    # Sort files by tf-idf
    sorted_tfidf = sorted([file for file in files], key=lambda x : tfidfs[x], reverse=True)

    # Return the 'n' top files that match the query
    return sorted_tfidf[:n]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    mwm_qtd = {sentence:{'mwm': 0, 'qtd': 0} for sentence in sentences}
    # Iterate through sentences and calculate total idfs
    for sentence in sentences:
        match = 0
        for word in query:
            if word in sentences[sentence] and word in idfs:
                # Sum up idfs
                mwm_qtd[sentence]['mwm'] += idfs[word]
                match += 1
        # Calculate sentence query term density
        mwm_qtd[sentence]['qtd'] = (match / len(sentence))

    # Sort by idf (primary) and qtd (secondary)
    sorted_sentences = sorted([sentence for sentence in sentences], key=lambda x: (mwm_qtd[x]['mwm'], mwm_qtd[x]['qtd']), reverse=True)
    # Return the 'n' top sentences that match the query
    return sorted_sentences[:n]

if __name__ == "__main__":
    main()
