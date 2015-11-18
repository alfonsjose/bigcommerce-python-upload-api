from collections import defaultdict
import itertools
from pprint import pprint
import time, datetime
import base64
import json 
import requests
import csv
from utilities import mycsv, csv_to_json, static_variables

class Connection(object):
    def request(self, method, url, *args):
        API_USER = 'alfons'
        API_KEY = '87886be9d3c84e6a37cf1c1c113092fd5229d861'
        auth = base64.b64encode(API_USER + ':' + API_KEY)
        headers = {'Authorization': 'Basic ' + auth, 'User-Agent': None, 'Connection': None,'Content-Type': 'application/json'}
        API_PATH = 'https://www.liveyoursport.com/api/v2'
        if args:           
            response = requests.request(method, API_PATH + url, headers=headers, data = args[0])           
        else: 
            response = requests.request(method, API_PATH + url, headers=headers)
        return response

class CSV_Parse(Connection):

    def __init__(self, filename):    
        """ Getting a Dictionary of Brands and their Brand IDs"""
        # a = Brands_Resource()  
        # self.brands_id_dict = a.get_brand_list()
        
        """ Getting a Dictionary of Categories and their Category IDs"""
        # c = Category_Resource()
        # self.category_id_dict = c.get_category_list()

        # print self.category_id_dict 

        """Testing Values"""        
        csv_file = csv.reader(open('Brand.csv','r'))
        self.brands_id_dict = {}
        for row in csv_file:
            self.brands_id_dict[row[0]] = row[1]
        csv_file = csv.reader(open('Categories.csv','r'))
        self.category_id_dict = {}
        
            
        c = 0
        for row in csv_file: 
            self.category_id_dict[int(row[1])] = {}
            self.category_id_dict[int(row[1])]['Category Name'] = row[0]

            """Creating a List of Parent IDs for each Category"""
            self.category_id_dict[int(row[1])]['Parent ID'] = []
            self.category_id_dict[int(row[1])]['Parent ID'].append([int(i.strip('[').strip(']').strip()) for i in row[2].split(',') ])       

        self.filename = filename
        self.in_stock_dict = {}

    def parse_csv(self):

        csv_list = csv_to_json.convert(self.filename)
        options_class = Options_Resource()
        # for i in range(54658,54673):
            # options_class.delete_options(i)
 
        for row in csv_list:
            try:
                print 'Time:', datetime.datetime.time(datetime.datetime.now())
                if row['Item Type'] == 'Product':
                    option_set_id, option_id_dict = None, None
                    product_name  = row['name']
                    product_class = Product_Resource(row, self.brands_id_dict, self.category_id_dict)               
                    options_class = Options_Resource()
                    Option_set_class = OptionSet_Resource()
                    rules_class = Rules_Resoruce()
                    sku_class = SKU_Resource()        
                    values_class = Option_Values_Resource()
                    option_set_option_class = Option_Set_Option_Resource()
                    rules_class = Rules_Resoruce()
                    product_id_dict,  sku_dict = {}, {}
                    if self.in_stock_dict:                                                             
                        sku_class.delete_SKU(self.in_stock_dict, sku_dict, product_id)
                        
                    product_id_dict, option_set_id = self.parse_productrow(row, product_class)
                    product_id = product_id_dict['id']

                    if not product_id_dict['New']:
                        print 'S'
                        sku_dict = sku_class.get_product_SKU(product_id)
                        print sku_dict
                        rules_dict = rules_class.get_product_rules(product_id)
                        
                elif 'SKU' in row['Item Type']:
                    if row['sku'] in sku_dict:
                        self.in_stock_dict[row['sku']] = sku_dict[row['sku']]                                       
                    else:
                        if option_id_dict == None:   
                            print 'option_id_dict None'                
                            option_values_dict = {}
                            option_id_dict = options_class.create_options(row, product_name)
                            print 'Option ID Dict'
                            print option_id_dict                            
                            for option_type, option_id in option_id_dict.iteritems():                        
                                option_set_option_class.create_option_set_option(option_id, option_type, option_set_id)

                        option_values_dict.update(values_class.create_option_values(option_id_dict, row))
                        
                        sku_id = sku_class.create_SKU(row, product_id, option_values_dict)

                elif 'Rule' in row['Item Type']:
                    if row['sku'] in sku_dict:
                        pass
                    else:
                        rules_class.create_rules(row, product_id, sku_id)
            except:
                pass    
        # print 'Deleting Product and Option Set'
        
        # delete = raw_input('Delete?')
        # if delete:

        #     for option_type, option_id in option_id_dict.iteritems():            
        #         options_class.delete_options(option_id)
            
        #     product_class.delete_product(product_id)        
        #     Option_set_class.delete_option_set(option_set_id)

    def parse_productrow(self, row, product_class):
        row = static_variables.products(row)                    
        product_id, option_set_id = product_class.parse_product(row)
        return product_id, option_set_id

    def sku_list(self, product_id):
        path = '/products/%s/skus.json?limit={count}' %product_id
        response = self.response('GET', path)

class Brands_Resource(Connection):

    def get_brand_list(self):
        path = '/brands/count.json'

        brand_count = self.request('GET', path).json()['count']

        pages = brand_count/250 + 1
        
        self.brands_id_dict = {}  
        mywriter = mycsv.make_csv('Brand')

        for page_num in range(1, pages + 1):
            path = '/brands.json?limit=250&page=' + str(page_num)
            response = self.request('GET', path)

            for brand in response.json():
                mywriter.writerow([brand['name'],brand['id']])                
                self.brands_id_dict[brand['name']] = brand['id']

    def get_brand_id(self, product_dict, brands_id_dict ):
        """Replacing Brand Names with corresponding ids from brands_id_dict"""
        for brand in brands_id_dict:
            if brand.strip().lower() == product_dict['brand_id'].strip().lower():
                 product_dict['brand_id'] = brands_id_dict[brand]
                 break
        else:            
            product_dict['brand_id'] = self.create_brand(product_dict['brand_id'])

        return product_dict

    def create_brand(self, brand_name) :
        """ Creating a new brand """
        create_dict =  {}
        create_dict['name'] = brand_name        
        create_dict['page_title'] = 'Buy %s at LiveYourSport.com. Amazing Discounts and massive range. Free Shipping.' %brand_name
        payload = json.dumps(create_dict)

        url = '/brands.json'
        response = self.request('POST', url, payload)
        print response
        print response.text
        new_brand_id = response.json()['id']
        print response
        return new_brand_id

    def delete_brand(self, brand_id):
        path = '/brands/%s' %brand_id
        response = self.request('DELETE',path)
        print response.text

class Category_Resource(Connection):

    def get_category_list(self):
        path = '/categories/count.json'
        categories_count = self.request('GET', path).json()['count']
        pages = categories_count / 250 + 1

        category_dict = {}

        for page_num in range(1, pages + 1):
            path = '/categories.json?limit=250&page=' + str(page_num)
            category_json = self.request('GET', path).json()
            for category in category_json:
                category_dict[category['name']] = category['id']

        return category_dict

    def get_category_id(self, product_dict, category_id_dict):
        """Replacing Category Names with corresponding ids from category_id_dict"""
        row  = []
        try:
            for index, cat in enumerate(product_dict['categories'].split(';')):            
                temp_list = []

                """Parsing Through Each category 'Level' of Front-End Categorization """

                for x, level in enumerate(cat.split('/')): 


                    """Comparing with the Category ID Dictionariy"""
                    for category_id, values in category_id_dict.iteritems():

                            if values['Category Name'].strip() == level.strip():             
                                
                                if not temp_list and len(values['Parent ID'][0])==1:                               
                                    temp_list.append(category_id)           
                                    
                                else:
                                    if set(temp_list) < set(values['Parent ID'][0]):                               
                                        temp_list = values['Parent ID'][0]

                row.append(temp_list[-1])
        except:
            pass

        product_dict['categories'] = row

        return product_dict


    def create_category(self):
        create_dict = {}
    
    def delete_category(self):
        pass

class Image_Resource(Connection):

    def __init__(self, product_dict):
        self.product_dict = product_dict

    def get_product_images(self, product_id):
        
        path = '/products/%s/images.json' %(product_id)
        response = self.request('GET', path)
        filename = 'Images_id%s.json' %product_id        
        product_json_file = open(filename,'w')        
        
        data = response.json()
        data = json.dumps(data)
        product_json_file.write(data)

    def create_images(self, product_id):
        """
        Creation of Product Image Resource for Upload and then Posts each image.
        """
        new_dict = {}        

        for key ,value in self.product_dict.iteritems():
            if 'Image File' in key and value != '' :                
                    image_dict = {}
                    image_dict['image_file'] = value
                    image_dict['description'] = ("Buy the %s Online in India at LiveYourSport.com."
                                                 " Free Shipping and Amazing Discounts"
                                                    %self.product_dict['name'].strip('*') 
                                                )                   
                    if '1' in key:
                        image_dict['is_thumbnail'] = True
                        image_dict['sort_order'] = 0
                    else:
                        image_dict['is_thumbnail'] = False
                    
                    payload = json.dumps(image_dict)
                    path = '/products/%s/images' %product_id                    
                    response = self.request('POST', path, payload)

class OptionSet_Resource(Connection):
    
    def __init__(self):
        self.count = 0

    def create_option_set(self, name):
        path = '/option_sets.json'
        option_dict = {'name':name}
        payload = json.dumps(option_dict)        
        response = self.request('POST', path, payload)        
    
        """If Option Set Exists"""
        if response.status_code>400:
            option_set_id = self.get_option_set_id(name)
            return option_set_id
        else:
            data = json.dumps(response.json())
            data = json.loads(data)            
            return data['id']

    def get_option_set_id(self, option_set_name):
        path = '/option_sets.json?name=%s' %option_set_name
        response = self.request('GET', path)
        data = response.json()
        data = json.dumps(data)
        data = json.loads(data)
        for k in data:            
            return k['id']
            break

    def delete_option_set(self, option_set_id):
        path = '/option_sets/%s' %option_set_id
        response = self.request('DELETE', path)
        print response
    
class Product_Resource(Connection):

    def __init__(self,  product_row, brands_id_dict, category_id_dict):
        self.brands_id_dict = brands_id_dict 
        self.category_id_dict = category_id_dict  

    def parse_product(self, product_dict):

        """ Assigning Brand ID """
        brands_class = Brands_Resource()
        product_dict = brands_class.get_brand_id(product_dict, self.brands_id_dict)
        
        """ Assigning Category ID"""
        category_class = Category_Resource()
        product_dict = category_class.get_category_id(product_dict, self.category_id_dict)

        """  Removing Non-Image Fields  """
        new_product_dict = {}
        for key,value in product_dict.iteritems():
            if 'Image' not in key:
                new_product_dict[key] = value

        """Creating a new Option Set"""
        option_class = OptionSet_Resource()
        self.option_set_id = new_product_dict['option_set_id'] = option_class.create_option_set(new_product_dict['name'])
        
        """ Creating a Product"""
        self.product_id_dict = self.create_products(new_product_dict)        

        """Creating Images for New Products"""
        if self.product_id_dict['New']: 
                img = Image_Resource(product_dict)
                img.create_images(self.product_id_dict['id'])

        return self.product_id_dict, self.option_set_id 

    def create_products(self, product_dict):
        del product_dict['id']
        del product_dict['Item Type']                                                
        path = '/products.json'
        payload = json.dumps(product_dict)
        response = self.request('POST', path, payload)
        product_id_dict = {}
        """If Product Exists"""
        if response.status_code>400:
            product_id_dict['id'] = self.update_product(product_dict)
            product_id_dict['New'] = False
        else:
            print 'Creating Product: ', product_dict['name']
            data = json.dumps(response.json())
            data = json.loads(data)        
            product_id_dict['id'] = data['id']        
            product_id_dict['New'] = True

        print product_id_dict
        return product_id_dict

    def delete_product(self,product_id):        
        path = '/products/%s'%product_id
        response = self.request('DELETE', path)
        print response

    def update_product(self, product_dict):
        path = '/products.json?name=%s' %product_dict['name']
        response = self.request('GET', path)
        print 'Updating Product', product_dict['name']
        
        for fields in response.json():
            return fields['id']
            break

    def get_product_ids(self, product_name):
        """Returns the Product ID and its Option Set ID based on the product's name"""

        path = '/products.json?name=%s' %product_name
        response = self.request('GET', path)
        response = response.json()
        for key in response:
            product_id = key['id']
            option_set_id = key['option_set_id']

        return product_id, option_set_id


        # else:
        #     path = '/products/%s.json' % product_id
        #     response = self.request('GET', path)
        #     filename = 'ID_%s.json' %product_id
        #     product_json_file = open(filename,'w')
        #     #
        #     data = response.json()
        #     data = json.dumps(data)
        #     product_json_file.write(data)
        #     return response.json()
 

class Option_Values_Resource(Connection):

    def __init__(self):
        self.label_list = []
        self.sort_order = 0

    def create_option_values(self, option_id_dict, values_dict):

        values_list = values_dict['name'].split(',')
        values_dict = {}
        values_id_dict = {}
        
        for values in values_list:
            self.sort_order +=1
            value_type = values.split('=')[0].split(']')[-1].strip()
            option_id = option_id_dict[value_type]
            values_dict['label'] = values.split('=')[-1].split(']')[-1].split(':h')[0].strip()
            
            """Checking if Option Value already exists"""
     
            if values_dict['label'] not in self.label_list:
                self.label_list.append(values_dict['label'])

                if 'http' in values:  
                    """For Thumbnail Images"""
                    values_dict['value'] = 'h'+values.split(':h')[-1].strip()
                else:
                    values_dict['value'] = values.split('=')[-1].strip()   

                # values_dict['sort_order'] =  self.sort_order
                payload = json.dumps(values_dict)
                path = '/options/%s/values.json' %option_id
                response = self.request('POST', path, payload)
                print response.text        
                values_id_dict[values_dict['label']] = response.json()['id']
            
        return values_id_dict
            
    def get_option_value(self, option_id):
        path = '/option/%s/values' %option_id
        response = self.request('GET', path)
        
        print response.text
        pprint(response.json())

class Options_Resource(Connection):

    def __init__(self):

        self.counter = 0
    
    def create_options(self, option_dict_params, product_name):
        
        path = '/options.json'
        values_dict = {}
        values_dict = option_dict_params

        options_list = option_dict_params['name'].split(',')

        option_dict , option_id_dict = {},{}
        

        for option in options_list:
            
            option_dict['display_name'] = option.split('=')[0].split(']')[-1]
            option_dict['name'] = product_name + option_dict['display_name']
            option_dict['type'] = option.split('=')[0].split(']')[0].strip('[')
            payload = json.dumps(option_dict)
            response = self.request('POST', path, payload)
            print response , response.text


            while int(response.status_code)>400:
                option_dict['display_name'] = option.split('=')[0].split(']')[-1]
                option_dict['name'] = product_name + option_dict['display_name']
                option_dict['type'] = option.split('=')[0].split(']')[0].strip('[')
                payload = json.dumps(option_dict)
                response = self.request('POST', path, payload)
                self.counter += 1 

                print response , response.text, "X"
                path = '/options.json?name=%s' %(option_dict['name'])
                response = self.request('GET', path)
                print response.json()                
                
                for k in response.json():
                    print k['id']
                    option_id = k['id']
                    break

                self.delete_options(option_id)


            
            option_id_dict[option_dict['display_name']] = response.json()['id']    
        
        return option_id_dict
            # option_id = 
            # options_class.delete_options(54088)


    def delete_options(self, option_id):
        path = '/options/%s' %option_id
        response = self.request('DELETE', path)
        print 'Deleting Option', response

    def get_options(self, product_id):
        path = '/products/%s/options.json' % (product_id)
        response = self.request('GET', path)
        return response.json()
            
class Option_Set_Option_Resource(Connection):

    def create_option_set_option(self, option_id, name, option_set_id):

        path = '/option_sets/%s/options.json' %option_set_id        
        payload = {}
        payload['option_id'] = option_id
        payload['display_name'] = 'Choose a %s' %name
        payload['is_required'] = True
        payload = json.dumps(payload)
        response =  self.request('POST', path, payload)

class Rules_Resoruce(Connection):

    def create_rules(self, rules_dict, product_id, sku_id):
        
        color = rules_dict['name'].split('Color')[-1].split('=')[-1].strip()
        conditions = {}
        conditions['sku_id'] = sku_id
        payload = {}
        payload['conditions'] = [conditions]
        payload['is_enabled'] = True
        payload['image_file'] = rules_dict['Product Image File - 1']
        payload = json.dumps(payload)
        path = '/products/%s/rules' %product_id
        response = self.request('POST', path, payload)

    def get_product_rules(self, product_id):
        path = '/products/%s/rules.json' %(product_id)
        response = self.request('GET', path)
        rules_dict = {}
        try: 
            for key in response.json():
                for xkey in key['conditions']:
                    rules_dict[xkey['sku_id']] = key['id']
        except:
            pass

        return rules_dict        



class SKU_Resource(Connection):

    def create_SKU(self, sku_row, product_id, option_values_dict):

        sku_list = sku_row['name'].split(',')        
        options_class = Options_Resource()
        product_options_json = options_class.get_options(product_id)
        option_list = []
        for sku in sku_list:
            value = sku.split('=')[-1].split(':ht')[0].strip()
            name = sku.split('=')[0].split(']')[-1].strip()

            options = {}
            options['option_value_id'] = option_values_dict[value]
            for product_option_dict in product_options_json:  
                if name in product_option_dict['display_name']:
                    options['product_option_id'] = product_option_dict['id']
                    break
            option_list.append(options)

        payload = {}
        payload['bin_picking_number'] = sku_row['bin_picking_number']
        payload['inventory_level'] = 100
        payload['sku'] = sku_row['sku']
        payload['options'] = option_list
        payload = json.dumps(payload)
        print 'Create SKU', payload
        path = '/products/%s/skus.json' %product_id
        response = self.request('POST', path, payload)
        print response.text

        return response.json()['id']

    def get_product_SKU(self, product_id):
        
        path = '/products/%s/skus.json' %(product_id)
        response = self.request('GET', path)
        print response.text, response
        sku_dict = {}
        for key in response.json():
            sku_dict[key['sku']] = key['id']
        return sku_dict

    def delete_SKU(self, in_stock_dict, sku_dict, product_id):
        for key, values in sku_dict.iteritems():
            if key not in in_stock_dict:
                path = '/products/%s/skus/%s' %(product_id, values) 
                response = self.request('DELETE', path)
                print response

        # for key in sku_dict:
        #     path = '/products/%s/skus/%s' %(product_id, key['id'])        
        #     response = connection.request('DELETE', path)
        #     print response.text

class deleting_products(Connection):

    def __init__(self, file_name):

        f = open(file_name)
        delete_file = csv.reader(f)
        id_list = []
        for row in delete_file:
            id_list.append(row[1])

        for product_id in id_list:
            print 'Deleting Product_ID: %s' %(product_id)
            try:
                self.delete_option_set(product_id)
                self.delete_options(product_id)
            except:
                pass

            path = '/products/%s' %product_id
            response = self.request('DELETE', path)
            print response.status_code, response.text

    def delete_option_set(self, product_id):

        path = '/products/%s.json' %(63129)
        response = self.request('GET', path)
        if response.status_code < 300:
            option_set_id = response.json()['option_set_id']
            path = '/option_sets/%s' %(option_set_id)
            response = self.request('DELETE', path)
            print response.status_code, response.text


    def delete_options(self, product_id):
        path = '/products/%s/options.json' %(63129)
        response = self.request('GET', path)

        for key in response:
            option_id = key['option_id']
            path = '/options/%s' %option_id
            response = self.request('DELETE', path)
            print response.status_code, response.text

        
# class outofstock(Connection):

#     def __init__(self,response):





if __name__ == '__main__':

    upload = CSV_Parse('DickSportingGoods2.csv')   
    upload.parse_csv()

    # connection =  Connection()
    # path = '/products.json?=bin_picking_number=DICKSPORTINGGOODS'
    # response =  connection.request('GET', path)
    
    # for k in response.json():
    #     print k['name'],k['bin_picking_number']
    # path = '/products/%s/rules.json'  %(100676)    
    # response = connection.request('GET', path)
    # # pprint(response.json())
    # for k in response.json():
    #     for x in k['conditions']:
    #         print x['sku_id'] = rules

#NOTES:
# - Option Set Fix. Eliminate and delete option sets if found
# - If product ID exists in the csv file 



    




