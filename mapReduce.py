from mrjob.job import MRJob
from mrjob.step import MRStep

class MRmyjob(MRJob):
	def mapper(self, _, line):
		wordlist = line.split(',')

		if wordlist[1] != 'Timestamp':
			yield (wordlist[2], 1) # return each entry's type, 1

	def reducer(self, key, list_of_values):
	 	yield key,sum(list_of_values) # add up how many times entry appears

if __name__ == '__main__':
    MRmyjob.run()




