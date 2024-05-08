import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Find which links page links to
    links = corpus.get(page)
    # Initialize empty dictionary
    dictionary = dict()
    # If page contains links
    if links is not None:
        #With probability `damping_factor`, choose a link at random linked to by `page`.
        p = damping_factor/len(links)
        # With probability `1 - damping_factor`, choose a link at random chosen from all pages in the corpus.
        remain = (1 - damping_factor)/(len(corpus))
        for link in links:
            dictionary[link] = p + remain
        for link in corpus:
            if link not in dictionary:
                dictionary[link] = remain
    # If no links in page
    else:
        p = 1/len(corpus)
        for link in corpus:
            # All pages have equal probability of being clicked
            dictionary[link] = p
    return dictionary
    

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize dictionary where each key is a page in the corpus
    pageranks = {page: 0 for page in corpus}
    click = 1/n
    # Randomly choose a page from the corpus as the first sample. 
    page = random.choice(list(corpus))
    pageranks[page] += click
    # Iterate n times
    for _ in range(1,n):
        # Update for each iteration
        model = transition_model(corpus, page, damping_factor)
        # Click on page given available links and the probabaility distributions
        page = random.choices(list(model.keys()), list(model.values()), k=1)[0]
        # Add a click to the pageranks dictionary
        pageranks[page] += click
    return pageranks

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    # Initialize dict where each page in corpus has p = 1/N
    PR = {page: (1/N) for page in corpus}
    new = {page: 0 for page in corpus}
    rand = (1-damping_factor)/N
    change = 1
    # Keep iterating until changes are less than 0.001
    while change >= 0.001:
        # Iterate through corpus
        for page in corpus.keys():
            summation = 0
            # Iterate through other pages in corpus
            for prev_page in corpus.keys():
                # A page with no links = page with 1 link to each page in corpus
                if len(corpus[prev_page]) == 0:
                    summation = 1/N
                # If the prev_page has a link to current page:
                elif page in corpus[prev_page]:
                    summation += (PR[prev_page]/len(corpus[prev_page]))
            p = rand + (damping_factor*summation)
            new[page] = p
        # Normalize values
        norm_factor = sum(new.values())
        new = {page: (rank / norm_factor) for page, rank in new.items()}
        # Calculate the largest change in value
        max = 0
        for _ in new:
            change = abs(new[page] - PR[page])
            if change > max:
                max = change
        # Update PR
        PR = new

    return PR            

if __name__ == "__main__":
    main()
