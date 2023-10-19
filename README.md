## Project Milestone 1

In this project milestone, you will piece together and extend many of the search engine features you have already programmed in this class. You will program an application to index a directory of files using a positional inverted index. You will then process the user's Boolean search queries on the index you constructed. The requirements for this project are enumerated in full detail below, written for 2-person teams which you are encouraged to form. You may work alone, but there will not be an adjustment in the expectations. 

### Requirements

#### Corpus
Your search engine should ask for a directory to load documents from when it begins. You should be able to load both .txt documents (as in the homework) and also .json documents; your project will be tested with the corpus contained in this ZIP file Download this ZIP fileOpen this document with ReadSpeaker docReader, which contains over 30,000 documents I copied from the National Parks Service website many years ago.

JSON documents are very different than the Moby Dick text documents: their title and content are both pulled from specific keys in the JSON data, rather than the content being the entire byte content of the file. This page will walk you through writing a JsonFileDocument class and using it to load .json documents into your existing search engine.

### Tokenization
Tokenize, process, and normalize the tokens of each document in the chosen corpus to form the terms of the search engine. Use the existing EnglishTokenStream for tokenization. Write a new derived-class of TokenProcessor that processes tokens into types and normalizes types into terms with two different methods. The "process token" method should convert a token into a type by:

If there is at least one hyphen (-) in the token:
Split the token to form 2 or more tokens.
Form a set containing the split tokens, as well as the original token with the hypen(s) removed.
Example: "Hewlett-Packard-Computing" turns into the set {Hewlett, Packard, Computing, HewlettPackardComputing}.
The remaining steps are performed on each token in the set, and the set of resulting types is returned. Note that this means the "process token" method now returns a list of string results, not just a single string.
Remove all non-alphanumeric characters from the beginning and end of the token, but not the middle.
Example: Hello. becomes Hello ; 192.168.1.1 remains unchanged.
Remove all apostrophes or quotation marks (single or double quotes) from anywhere in the token.
Convert the token to lowercase.
Add a "normalize type" method to your TokenProcessor class, which converts a type into a term by:

Stem the using a "Porter2 Stemmer". Please do not code this yourself; find an implementation with a permissible license and integrate it with your solution.
The terms are inserted into the inverted index. Types are only used for wildcard queries and spelling correction; they can be discarded if you are not implementing those.

 
### Indexing
You will maintain one index for your corpus: the PositionalInvertedIndex, a positional index as discussed in class, where postings lists consist of (documentID, [position1, position2, ...]) pairs. Using InvertedIndex from Homework 2 as a reference point, create PositionalInvertedIndex as a new implementation of the Index interface. We will no longer have a need for positionless postings, so the Posting class will need to be updated to represent the list of positions of a posting. You will also need to modify addTerm to account for the position of the term within the document. 

The index should consist of a hash map from string keys (the terms in the vocabulary) to (array) lists of postings. You must not use any other hash maps or any “set” data structures in your code, only lists.

 

### Boolean Querying
The search engine will support queries of the form 
, where the + represents "OR", and spaces separating words indicate "AND". Each 
 is a "subquery" consisting of one or more query literals separated by white space. A query literal is either:

a single token (a TokenLiteral)
a sequence of tokens contained within double-quotes, representing a phrase (a PhraseLiteral)
Examples:

shakes "Jamba Juice"
Documents that contain both "shakes" and also the phrase "Jamba Juice".
shakes + smoothies mango
Documents that contain "shakes" OR "smoothies" and also "mango".
I have written for you a sophisticated BooleanQueryParser class, with a method parseQuery. Given a string of this format, the parser returns a tree of QueryComponent objects, representing the abstract syntax tree of the query as shown in lecture. The method getPostings, when provided an Index that you built, will return a list of postings that satisfy the query... well, once the parser is finished, that is.

There are three classes you must modify to meet the Acceptable Query requirements, finishing the getPostings method for each. These classes represent one piece of the abstract syntax tree. 

TermLiteral: represents a single term. To getPostings, we simply go to the provided Index and retrieve the postings for the TermLiteral object's string.
AndQuery: stores a list of two or more query components, whose postings must be merged with the "AND" merge. To finish getPostings, we must get the postings of the first two query components contained in the AndQuery, then merge them with the algorithm from lecture. If there is another query component, we retrieve its postings and merge it with the previous result. Repeat this process until all the components contained in the AndQuery have been merged.
OrQuery: similarly, stores a list of two or more query components that must be "OR" merged.
In your main, after retrieving the postings for the query, print out the titles and IDs of the documents that were returned. 

### Additional Requirements
You have several choices on how to achieve a higher score on the project. Some options are not available until Milestone 2; they are not listed here. 

#### Corpus
Extend the FileDocument class to load a third format of document. It must be something complicated like XML, HTML, Word, or PDF, which require special rules to integrate with our search engine. 

You will also have an option on Milestone 2 to receive an Excellent on your Corpus grade.

#### Tokenization
Write specialized code for dealing with a non-English language corpus (which you must also locate). There must be a reasonable level of complexity to your solution; check with me first. Alternatively, use a Natural Language Processing library to tokenize text, mapping its output to the form expected by our search engine, and utilize its token metadata in some way.

#### Indexing
By design, you can only achieve Good or Excellent in this category during Milestone 2. You can get a head start on that task by implementing a k-gram index or a Soundex index, outlined in chapter 3.4.

#### Boolean Querying
Implement getPostings in two more query classes to earn a Good on this requirement:

PhraseLiteral: contains a list of two or more query components that are expected to be in subsequent positions. Let k=1. Retrieve postings for the first two components in the phrase, and look for documents that are in both similar to an AND merge. If a document is found, examine the positions next, looking for a position in the first list that is equal to a position in the second list minus k. If found, retain that document and the correct position(s). Like with an AndQuery, continue to get postings for each subsequent component in the phrase, increasing k each loop. The book has an implementation of this algorithm in pseudocode.
NotQuery: you don't have to modify this class, which stores a single query component that should be "AND NOT" merged with another. Instead, you must modify AndQuery's merge to perform different logic if the second component in the merge is a "negative" component (see the NotQuery class). We will use a dash in front of a query literal to indicate "not".
Implement either wildcard queries (using a k-gram index) or author queries (where you search for documents based on their author, using the Soundex index from chapter 3.4), in addition to the above, for an Excellent grade on this requirement.

Quality & Ambition
You cannot directly earn points on this requirement, unless you are going for Excellent, in which case you can start planning a difficult addition to the search engine such as spelling correction or a graphical user interface. Speak to the instructor first.

## Project Milestone 2

### Requirements

### Indexing (update)
To earn a Good, you must build an index on disk, and only read postings for the terms needed to satisfy a query. (I.e., you cannot read the entire index back into memory.) You must follow the format developed in lecture: dft, doc id, tftd, positions, repeated; using gaps for document IDs and positions.

You must ALSO compute the length of each document, L_d, during indexing time, and save those values on disk to a file docWeights.bin in document ID order. To compute L_d for a given document d, you must add up the square of the values for each term in that document, and then take the square root of that sum. (This is the Euclidian length of the document's vector.) This 8-byte floating point value should be written to docWeights.bin.

You will create a new Index class, DiskPositionalIndex, for reading postings from a disk index file. See the document from earlier for details. This class should have two methods for reading postings: one that includes positions, and one that skips over them (since only phrase queries require positions, all other Boolean and ranked query objects should not read positions from disk).


#### DiskIndexWriter
Create a class called DiskIndexWriter. Write a method writeIndex taking parameters for an existing, initialized in-memory PositionalInvertedIndex, along with a path of where to save the on-disk index. In the method, you will need to create/open a file in binary mode to store your postings; I recommend calling it postings.bin. In Java, you should use the RandomAccessFile class to open the file; in Python, use open(..., "rb"); and in C++, create an ofstream object and use .open(..., ios::binary)

Retrieve the vocabulary from the index, and loop through each term in the vocab list. Get the postings list for a term, then write the list to disk using our format: first dft, then a doc id gap, then tftd, then a bunch of position gaps, repeating. Easy!

Java: use writeInt
Python: use write along with struct.pack (look it up)
C++: you may want to ensure your bytes are in big-endian order, and rearrange if not; then use .write().

As you finish each term in the vocabulary, you will want to record the byte position of where the postings for that term started. That information needs to be stored in a database; you can use SQLite if you don't know any other library. 

#### DiskPositionalIndex
Create a new class DiskPositionalIndex that extends your Index interface. You should construct a DiskPositionalIndex with a path identifying where its files are located. The index can open those files, but should not read them until postings are actually needed, and even then should only read the data for the required index term, and NOT just read the entire index at once.

To implement getPostings(String term):

1. Use your database to load the byte position of where the term's postings begin.
2. Using your already-opened postings.bin file, seek to the position of the term.
3. Using readInt (Java), read() w/ struct.unpack (Python), or .read() (C++), read dft, then docid gap, then tftd, then position gap, etc. etc. As values are read, construct in-memory Posting objects to store the information, then return a List of Postings when you have read everything you need from disk.

Nothing in your Query code should change. You will simply pass your DiskPositionIndex to QueryComponent.getPostings, and the components themselves will just call getPostings on your index to do their merges. They don't care where the postings come from!

### Ranked Querying
Besides on-disk indexing, this is the major focus of milestone 2. 

Add a mode to your search engine to ranked query an on-disk index. Write a method to perform ranked retrieval on a given index for a given set of query terms, by implementing the loop from class:

* for each term t in the query:
	* Calculate wqt, using the formula 
	* For each document d in t's postings list:
		* Calculate 
		* Acquire an accumulator A_d for document d
		* Increase the accumulator by 
* for each accumulator A_d:
	* divide A_d by L_d, which your DiskPositionalIndex class should be able to read from your docWeights.bin file.
	* put the quotient into a priority queue
* Using the priority queue, return the top 10 documents and their scores.

When printing a ranked query to the user, please include document titles as well as the score assigned that document. 


