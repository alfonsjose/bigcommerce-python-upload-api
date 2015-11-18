import unicodecsv, itertools
import csv
import json
from pprint import pprint


def convert(filename):
    csv_file = csv.reader(open(filename, 'r'))
    fieldnames = fieldname_generator(csv_file)
    
    """ Dictionary object containing headers 
            formatted as the API keys and values from the read csv
    """

    csv_file = open(filename, 'r')
    csv_dict = csv.DictReader(csv_file, fieldnames)     

    return csv_dict
    # json_data  = json.dumps([r for r in csv_dict])

""""Writing JSON File from read CSV"""
# json_file = open('Json_Book1.json', 'w')
# data  = json.dumps([r for r in csv_dict])
# json_data = json.load(data)
# json_file.write(data)

# with open("Json_Book1.json") as json_file:
# json_data = json.load(json_file)

def fieldname_generator(csv_file):
    # Entering Field Name, Headers
    for row in csv_file:
        dict_headers = row
        break

    """ Dictionary containing CSV Field Names as Keys and 
        corresponding BigCommerce JSON Field Names as values
    """

    replace_dict = {  
        'Product Name': 'name',
        'Product Code/SKU': 'sku',
        'Product ID': 'id',
        'Brand Name': 'brand_id',
        'Price': 'price',
        'Sale Price': 'sale_price',
        'Retail Price': 'retail_price',
        'Cost Price': 'cost_price',
        'Product Description': 'description',
        'Bin Picking Number': 'bin_picking_number',
        'Category': 'categories',
        'Product Availability': 'availability_description',
        'Current Stock Level': 'inventory_level',
        'Free Shipping': 'is_free_shipping',
        'Sort Order': 'sort_order',
        'Meta Description': 'meta_description',
        'Page Title': 'page_title',
        'Track Inventory': 'inventory_tracking'
        
    }

    for index,name in enumerate(dict_headers):        
            for k, v in replace_dict.iteritems():
                if k in name:
                    dict_headers[index]  = name.replace(k, v)
                    break

    fieldnames = tuple(dict_headers)
    return fieldnames


