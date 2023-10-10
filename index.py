import os
import string
import nltk
import time
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import digits
from bs4 import BeautifulSoup


def index_documents(directory="./HTMLDocuments"):

    """
    Loops through each individual document and assigns it a unique id.
    :param directory: Specified directory to loop through, by default will loop through the HTML documents directory.
    :return: A dictionary containing each document and it's unique identifier.
    """

    retrieved_files = os.listdir(directory)
    dictionary = {i: x for i, x in enumerate(retrieved_files, 0)}
    return dictionary


def save_indexed_documents():

    """
    Write all indexed documents to a text file called: "documents.txt
    :return: Returns an array of indexed documents.
    """

    indexed_documents = index_documents()
    for document_id, document in indexed_documents.items():
        print(f"Successfully indexed the document: {document} with the ID: {document_id}")
        write_information("documents.txt", f"{document_id} : {document} \n")
    return indexed_documents


def prepare_hero_name(hero_name):

    """
    Manipulates the specified string in this case the hero name to be able to search through the vocabulary table for
    the correct id to use to correspond with the postings table.
    :param hero_name: Specified hero name that we'll manipulate to be searchable.
    :return: Returns a manipulated hero name suitable for searching.
    """

    new_name = hero_name.replace(" ", "")
    newer_name = new_name.replace("-", "")
    if "[" in newer_name:
        newer_name = newer_name.split("[")[0]
    elif "(" in newer_name:
        newer_name = newer_name.split("(")[0]

    cleaned_text = clean_text(newer_name)
    cleaned_digits = clean_digits(cleaned_text)
    return cleaned_digits


def index_vocabulary(document):

    """
    Searches through all paragraphs contained within the document and indexes the vocabulary after being cleaned.
    :param document: The BeautifulSoup document to traverse for vocabulary.
    :return: Returns a list of vocabulary.
    """

    stop_words = set(stopwords.words("english"))
    hero_name = document.select(".pi-data-value")[0].text
    prepared_hero_name = prepare_hero_name(hero_name)
    all_paragraphs = [i.text for i in document.find_all("p")]
    cleaned_paragraphs = [clean_text(i) for i in all_paragraphs]
    adjusted_paragraphs = [clean_digits(i) for i in cleaned_paragraphs]
    cleaned_split_terms = [p.split() for p in adjusted_paragraphs]
    lowered_unique_terms = set([str(v).lower() for t in cleaned_split_terms for v in t])
    stop_adjusted_terms = [t for t in lowered_unique_terms if t not in stop_words]
    stop_adjusted_terms.append(prepared_hero_name.lower())
    return stop_adjusted_terms


def retrieve_all_vocabulary():

    """
    Retrieves all vocabulary from all HTML documents.
    :return: Returns dictionary containing all vocabulary.
    """

    html_documents = retrieve_directory_files("./HTMLDocuments")
    vocabulary_list = []
    for document in html_documents:
        read_file = open("./HTMLDocuments/" + document, encoding="utf8").read()
        parsed_document = BeautifulSoup(read_file, "html.parser")
        vocabulary_list.append(index_vocabulary(parsed_document))
        print(f"Successfully indexed the vocabulary of {document}")
    duplicates_removed_list = list(dict.fromkeys([v for t in vocabulary_list for v in t]))
    vocabulary_dictionary = {i: x for i, x in enumerate(duplicates_removed_list, 0)}
    return vocabulary_dictionary


def save_indexed_vocabulary(vocabulary_dictionary):

    """
    Writes all indexed vocabulary to a text file called: vocabulary.txt
    :param vocabulary_dictionary: The vocabulary dictionary to write.
    :return: Returns the vocabulary dictionary.
    """

    for key, value in vocabulary_dictionary.items():
        write_information("vocabulary.txt", f"{key} : {value} \n")
    return vocabulary_dictionary


def construct_postings_table_base(postings_table, vocabulary_table):

    """
    Constructs the initial base for the postings table so information can be inserted
    :param postings_table: Empty dictionary for postings table to be created upon.
    :param vocabulary_table: Vocabulary table to know how many items to create.
    :return: Returns the constructed posting table base.
    """

    for key, _ in vocabulary_table.items():
        postings_table[key] = []
    return postings_table


def construct_postings_table(postings_table, document, vocabulary_table, document_table):

    """
    Performs the main construction of the postings table, traversing all information and inserting it into the postings
    table.
    :param postings_table: The base postings table to insert information into.
    :param document: The document to traverse in this instance.
    :param vocabulary_table: The vocabulary table to extract IDs from.
    :param document_table: Document table to extract IDs from.
    :return: returns a filled postings table.
    """

    stop_words = set(stopwords.words("english"))
    document_name = f"{extract_document_title(document)}.html"
    all_paragraphs = [i.text for i in document.find_all("p")]
    cleaned_paragraphs = [clean_text(i) for i in all_paragraphs]
    adjusted_paragraphs = [clean_digits(i) for i in cleaned_paragraphs]
    cleaned_split_terms = [p.split() for p in adjusted_paragraphs]
    lowered_unique_terms = set([str(v).lower() for t in cleaned_split_terms for v in t])
    stop_adjusted_terms = [t for t in lowered_unique_terms if t not in stop_words]

    document_id = extract_dictionary_key(document_table, document_name)
    for term in stop_adjusted_terms:
        determined_term_id = extract_dictionary_key(vocabulary_table, term)
        postings_document_list = postings_table[determined_term_id]
        if document_id not in postings_document_list:
            postings_document_list.append(document_id)
        postings_table[determined_term_id] = postings_document_list

    return postings_table


def create_postings_table():

    """
    The final construction of the table, taking all elements to create the postings table from all documents,
    accounting for all vocabulary and documents
    :return: Returns the fully constructed posting table.
    """

    html_documents = retrieve_directory_files("./HTMLDocuments")
    indexed_documents = index_documents()
    indexed_vocabulary = retrieve_all_vocabulary()
    postings_table_dictionary = {}
    constructed_postings_table = construct_postings_table_base(postings_table_dictionary, indexed_vocabulary)
    finished_postings_table = {}
    for document in html_documents:
        read_file = open("./HTMLDocuments/" + document, encoding="utf8").read()
        parsed_document = BeautifulSoup(read_file, "html.parser")
        finished_postings_table = construct_postings_table(constructed_postings_table, parsed_document, indexed_vocabulary, indexed_documents)
    return finished_postings_table


def save_postings_table():

    """
    Write the postings table to a text document called "postings.txt"
    :return:
    """

    postings_table = create_postings_table()
    for key, value in postings_table.items():
        write_information("postings.txt", f"{key} : {value} \n")


def clean_text(specified_text):

    """
    Cleans the specified string of punctuation.
    :param specified_text: String you wish to clean of punctuation.
    :return: Returns a string void of punctuation.
    """

    cleaned_string_table = specified_text.maketrans("", "", string.punctuation)
    cleaned_string = specified_text.translate(cleaned_string_table)
    return cleaned_string


def clean_digits(specified_text):

    """
    Cleans the specified string of digits.
    :param specified_text: String you wish to clean of digits.
    :return: Returns a string void of digits.
    """

    cleaned_string_table = specified_text.maketrans("", "", digits)
    cleaned_string = specified_text.translate(cleaned_string_table)
    return cleaned_string


def extract_string_occurrences(term_detection_list, text):

    """
    Extracts a list of specified strings from a specified text and returns a dictionary of their occurrences.
    :param term_detection_list: The list of terms you wish to detect.
    :param text: The text you wish to traverse.
    :return: A dictionary containing the occurrences of the specified strings.
    """

    cleaned_string_table = text.maketrans("", "", string.punctuation)
    cleaned_string = text.translate(cleaned_string_table)
    lowered_terms = [term.lower() for term in cleaned_string.split(" ")]
    dictionary = {term: lowered_terms.count(term.lower()) for term in term_detection_list}
    return dictionary


def extract_dictionary_key(dictionary, value):

    """
    Extracts a key from a specified dictionary based on it's corresponding value.
    :param dictionary: The dictionary you wish to traverse for the key.
    :param value: The value you wish to find the corresponding key to.
    :return: Returns the key corresponding to the value.
    """

    placeholder_array = [k for k, v in dictionary.items() if v == value]
    return placeholder_array[0]


def extract_document_title(document):

    """
    Extracts the document title from the HTML content to be used in constructing the file name.
    :param document: The document of which you wish to extract the name from.
    :return: Returns the name of the document.
    """

    raw_document_name = document.select(".page-header__title")[0].text
    raw_document_name_table = raw_document_name.maketrans(" ", "_")
    document_name = raw_document_name.translate(raw_document_name_table)
    prepared_document_name = document_name.strip()
    return prepared_document_name


def construct_hero_information(document):

    """
    Retrieves all specific hero information from the document and stores it in a dictionary.
    :param document: The document from which you wish to extract the information.
    :return: Returns the dictionary of information corresponding to the hero.
    """

    labels = [i.text for i in document.select(".pi-data-label")]
    values = [i.text for i in document.select(".pi-data-value")]
    zip_iterator = zip(labels, values)
    constructed_map = dict(zip_iterator)
    return constructed_map


def save_hero_information():

    """
    Fetches all hero information from each individual document and saves it to a text file called: "heroes.txt"
    :return: Returns the dictionary of constructed information.
    """

    html_documents = retrieve_directory_files("./HTMLDocuments")
    constructed_hero_information = {}
    for document in html_documents:
        read_file = open("./HTMLDocuments/" + document, encoding="utf8").read()
        parsed_document = BeautifulSoup(read_file, "html.parser")
        hero_information = construct_hero_information(parsed_document)
        constructed_hero_information = hero_information
        for key, value in hero_information.items():
            write_information("heroes.txt", f"{key} : {value} \n")
        write_information("heroes.txt", "\n")
    return constructed_hero_information


def search_for_hero(postings_table, vocabulary_table, document_table, specified_hero_name):

    """
    Function to search for a hero and display all of the documents from which it appears in.
    :param postings_table: Postings table to search through.
    :param vocabulary_table: Vocabulary table to search through.
    :param document_table: Document table to search through
    :param specified_hero_name: The hero name you wish to search for.
    :return: (void) Displays a list of documents from which the hero appears in
    """

    manipulated_hero_name = prepare_hero_name(specified_hero_name)
    retrieved_term_id = extract_dictionary_key(vocabulary_table, manipulated_hero_name.lower())
    document_ids = postings_table[retrieved_term_id]
    retrieved_documents = [extract_dictionary_key(document_table, document_id) for document_id in document_ids]
    display_list(retrieved_documents)


def retrieve_directory_files(specified_directory=os.getcwd()):

    """
    Retrieves all files in a specified directory, by default gets the current working directory.
    :param specified_directory: Directory you wish to search in.
    :return: Returns a list of files.
    """

    return os.listdir(specified_directory)


def write_information(file_name, content):

    """
    Appeneds content to a specified file.
    :param file_name: The file name you wish to create/append content to.
    :param content: The content you wish to write/append to the file.
    :return: void
    """

    file = open(file_name, "a", encoding="utf8")
    file.write(content)
    file.close()


def display_dictionary(specified_dictionary):

    """
    Displays all information in a dictionary in a Key : Value format.
    :param specified_dictionary: The dictionary you wish to traverse.
    :return: void
    """

    for k, v in specified_dictionary.items():
        print(f"{k} : {v}")


def display_list(specified_list):

    """
    Displays all information in a list
    :param specified_list: The list you wish to traverse.
    :return: void
    """

    for v in specified_list:
        print(v)


def main():

    # Write out hero information to a file:
    save_hero_information()

    # Write out document IDs to a file:
    save_indexed_documents()

    # Write out vocabulary IDs and terms to a file:
    save_indexed_vocabulary(retrieve_all_vocabulary())

    # Write out postings table to a file:
    save_postings_table()

    postings_table = create_postings_table()
    indexed_documents = index_documents()
    indexed_vocabulary = retrieve_all_vocabulary()
    search_for_hero(postings_table, indexed_vocabulary, indexed_documents, "Thor Odinson")


if __name__ == "__main__":
    main()
