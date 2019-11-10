import requests
import aiohttp
import asyncio

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


async def get_package_details(session, name):
	"""Gets project details of a specific package as per: 
		https://warehouse.pypa.io/api-reference/json/
	
	Args:
		session: aiohttp.ClientSession, session used to send HTTP request 
		name: str, the name of the package
	"""

	# keep list of things retrieved
	stuff_got = []

	# get list of projects asynchronously:
	async with session.get(f'{PROJECT_BASE}/{name}/json') as response:
		status_code = response.status
		
		# if the status is 404 (i.e. we can't find the project) return 'None'
		if status_code == 404:
			return 0
		else:
			# else, return the json response
			response = await response.json()
			return float(len(response['info']['classifiers']))


async def run(package_list):
	# for each package's name:
	#	- get the details
	#	- and count the number of classifiers
	#	- save number to the dict below & keep a running tally
	i = 0
	packages = {}
	running_tally = 0.0
	tasks = []
	responses = None

	# fetch all responses within one Client session,
	# keep connection alive for all requests.
	async with aiohttp.ClientSession(headers=HEADERS) as session:
		for name in package_list:
			task = asyncio.ensure_future(get_package_details(session, name))
			tasks.append(task)
		responses = await asyncio.gather(*tasks)

	# now gathe responses
	running_tally += float(sum(responses))

	# get some calculations
	running_tally = float(running_tally)
	total_packages = float(len(package_list))
	avg_classifiers = float(running_tally / total_packages)
	print(f'Total number of projects: {len(package_list)}')
	print(f'Average number of classifiers: {avg_classifiers}')

def main():
	
	# first, get the asynchronous loop
	loop = asyncio.get_event_loop()

    # next, get the list of packages
	package_list = get_list_of_all_packages()
	# package_list = package_list[:500]

	# set-up the asynchronous tasks
	future = asyncio.ensure_future(run(package_list))
	loop.run_until_complete(future)


if __name__ == '__main__':
	main()
