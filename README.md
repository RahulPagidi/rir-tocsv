# Use Rossum's Invoice Robot to convert invoice files to a CSV table
Install dependencies in `requirements.txt` to make sure you get the required `magic` module from the right package.  
The script `folder2csv.py` works with Python 3.

## Example to process all invoices in a given folder:
```shell
ls <processed_invoices_folder> | folder2csv.py <path_to_csv_file> <api_key> <server_address>
```
