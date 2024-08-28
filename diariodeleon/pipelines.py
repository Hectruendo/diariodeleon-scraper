import json
from datetime import datetime

from itemadapter import ItemAdapter


class DiariodeleonPipeline:
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline:
    def open_spider(self, spider):
        # Get the current date in YYYYMMDD format
        date_str = datetime.now().strftime("%Y%m%d")
        # Create the file name with the date
        file_name = f"results/items_{date_str}.jsonl"
        # Open the file for writing
        self.file = open(file_name, "w")

    def close_spider(self, spider):
        # Close the file when spider is done
        self.file.close()

    def process_item(self, item, spider):
        # Convert the item to a JSON string and write it to the file
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)

        return item
