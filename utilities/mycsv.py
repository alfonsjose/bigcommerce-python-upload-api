import unicodecsv
brand_list, id_list = [] , [] 

def make_csv(name):
	""" returns mywriter """
	header = ['%s Name' % name, 'ID']
	output = open('%s.csv' % name, 'wb')
	mywriter = unicodecsv.writer(output)
	mywriter.writerow(header)
	return mywriter

def make_brand_list():
	f = open("Brand.csv")
	csv_file = csv.reader(f)
	for row in csv_file:
	    	brand_list.append(row[0])
    		id_list.append(row[1])



def get_brand_id(brand_name):
	print brand_list,id_list

   

