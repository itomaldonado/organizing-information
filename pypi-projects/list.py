import requests

from lxml import html

# variables
BASE='https://pypi.org'
SIMPLE=f'{BASE}/simple'
PROJECT_BASE=f'{BASE}/pypi'
HEADERS={'Accept': 'appliaction/json'}


def get_list_of_all_packages():
	"""Gets a list of all PyPI packages as per: https://warehouse.pypa.io/api-reference/legacy/"""
	# get list of projects:
	r = requests.get(SIMPLE, headers=HEADERS)
	package_list = [package for package in html.fromstring(r.content).xpath('//a/text()')]
	return package_list


def get_package_details(name):
	"""Gets project details of a specific package as per: 
		https://warehouse.pypa.io/api-reference/json/
	
	Args:
		name: str, the name of the package
	"""
	# get list of projects:
	try:
		r = requests.get(f'{PROJECT_BASE}/{name}/json', headers=HEADERS)
		
		# if we can't find the project, return None
		if r.status_code == 404:
			return None

		# return the json response
		return r.json()
	except Exception as e:
		print(f'Error with: {name}')
		print(f'Response: {r.text}')
		raise e



def main():
	# first, get the list of packages
	package_list = get_list_of_all_packages()

	# for each package's name:
	#	- get the details
	#	- and count the number of classifiers
	#	- save number to the dict below & keep a running tally
	i = 0
	packages = {}
	running_tally = 0.0
	for name in package_list:
		package = get_package_details(name)
		
		# if the package is missing, we count it as '0' classifiers
		if package:
			number_of_classifiers = len(package['info']['classifiers'])
		else:
			number_of_classifiers = 0
		
		packages.update({name: number_of_classifiers})
		running_tally += float(number_of_classifiers)
		i += 1

		if (i % 100) == 0:
			print(f'Done with: {i} projects - Last: {name}')

	# get some calculations
	running_tally = float(running_tally)
	total_packages = flooat(len(package_list))
	avg_classifiers = float(running_tally / total_packages)
	print(f'Total number of projects: {len(package_list)}')
	print(f'Average number of classifiers: {avg_classifiers}')


if __name__ == '__main__':
	main()
