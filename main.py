import csv
import datetime
import os
import re
from collections import Counter

from documentcloud import DocumentCloud
from documentcloud.addon import AddOn

class NGramCounter(AddOn):
    """A DocumentCloud Add-On that counts the frequency of specified n-grams in a document's text."""

    def main(self):
        if not self.documents:
            self.set_message("Please select at least one document.")
            return

        # Read in the list of n-grams to search for from the CSV file
        ngrams_to_search = []
        with open('exemptions.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                ngrams_to_search.append(row[0])

        # Loop through selected documents
        for document in self.documents:
            # Extract the creation date or use the upload date
            if document.created_at:
                document_date = datetime.datetime.strptime(document.created_at[:10], '%Y-%m-%d').date()
            else:
                # If no creation date, use the upload date and add a note
                document_date = datetime.datetime.strptime(document.updated_at[:10], '%Y-%m-%d').date()
                note = "Note: A creation date could not be automatically extracted for this document. " \
                       "The upload date is being used as the date for this analysis."
                self.client.notes.create(document.id, note)
                self.client.documents.update(document.id, {'data': {'date': str(document_date)}})

            # Get the document text
            text = document.full_text.decode('utf-8')

            # Clean the text by removing numbers, special characters, and extra white space
            text = re.sub(r'\d+', '', text)
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip().lower()

            # Count the occurrences of each n-gram in the text
            ngram_counts = Counter()
            for ngram in ngrams_to_search:
                count = text.count(ngram)
                ngram_counts[ngram] = count

            # Create a bar chart of the n-gram frequencies using Matplotlib
            import matplotlib.pyplot as plt
            plt.bar(range(len(ngram_counts)), list(ngram_counts.values()), align='center')
            plt.xticks(range(len(ngram_counts)), list(ngram_counts.keys()))
            plt.xticks(rotation=90)
            plt.title(f"N-Gram Frequency for {document.title} ({document_date.strftime('%Y-%m-%d')})")
            plt.xlabel("N-Gram")
            plt.ylabel("Frequency")
            plt.tight_layout()

            # Save the chart as an image file
            image_filename = f"{document.id}_ngram_frequency.png"
            plt.savefig(image_filename)

            # Upload the image file to DocumentCloud
            self.upload_file(image_filename)

            # Remove the image file from the local directory
            os.remove(image_filename)

        self.set_message("N-Gram frequency analysis complete.")
