from .postionalinvertedindex import PositionalInvertedIndex
class DiskIndexWriter:
    def __init__(self):
        pass

    def writeIndex(self, p_i_index, on_disk_index_path):
        """
        Writing the on-disk index.
        """
        # Creating / opening a file in binary mode in the specified path to write the positngs of the on-disk index.
        postings_file_path = on_disk_index_path + "\postings.bin"
        postings_file = open(postings_file_path, "rb")
        vocab = p_i_index.getVocabulary()
        for term in vocab:
            pass