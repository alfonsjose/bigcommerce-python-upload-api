from pprint import pprint

def products(product_dict):
    
    product_dict['type'] = 'physical'
    product_dict['page_title'] = ('Buy the %s at LiveYourSport Online in India. '
    							  'Massive Discounts and Amazing Range on %s. '
    							  'Free Shipping all across India' 
    							  %(product_dict['name'].strip('*'), product_dict['brand_id'].strip('*'))
    							 )


    product_dict['meta_description'] = ('Get your hands on the %s at LiveYourSport. '
										'Massive Discounts and Amazing Range on %s. '
										'Free Shipping all across India' 
										%(product_dict['name'].strip('*'), product_dict['brand_id'].strip('*'))
										)
    

    product_dict['is_visible'] = True
    product_dict['availability'] = 'available'
    product_dict['weight'] = '0'
    product_dict['is_free_shipping'] = False

    if 'Option' in product_dict['inventory_tracking']:
        product_dict['inventory_tracking'] = 'sku'
    else:
        product_dict['inventory_tracking'] = 'simple'
    
    if product_dict['retail_price'] == product_dict['sale_price']:
    	del product_dict['sale_price']

    del product_dict['Option Set']
    try:
        del product_dict['Allow Purchases']
    except:
        pass

    return product_dict


def image(image_dict):
	pass

def rules(rules_dict):
    
	
    pprint(rules_dict)

    return None
    # new_dict['is_enabled'] = True
    # new_dict['image_file'] = rules_dict['Product Image File - 1']


