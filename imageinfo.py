#!/usr/bin/python

##### Horrible code below. Sorry.
##### chris.leat@gmail.com
#####

import re
import binascii
import struct
import sys


class imageInfo:
	def __init__(self, f):
		self.f = f
		self.Catfishmagic = binascii.unhexlify('4361746669736820')
		self.Darwinkernelmagic = binascii.unhexlify('44617277696E204B65726E656C2056657273696F6E')
		self.OffsetedK = 1024
		self.Offseted = 0
		self.OffsetSegment = 0
		self.chunk_size = 1024
		
		
	def read_in_chunks(self, file_object):
		while True:
			data = file_object.read(self.chunk_size)
			if not data:
				break
			yield data

	def catfishSearch(self, f):
		filename = open(f, 'rb')
		for piece in self.read_in_chunks(filename):
			if re.search(self.Catfishmagic, piece):
				page = self.Offseted
				segment = piece.find(self.Catfishmagic)
				CatfishLocation = page + segment
				break
			self.Offseted = self.Offseted + self.chunk_size
		for piece in self.read_in_chunks(filename):	
			if re.search(self.Darwinkernelmagic, piece):
				pageK = self.OffsetedK
				segmentK = piece.find(self.Darwinkernelmagic)
				DarwinKernelLocation = pageK + segmentK
				locationOfDarwinString = DarwinKernelLocation + CatfishLocation
				break
			self.OffsetedK = self.OffsetedK + self.chunk_size

		locationOfOSBuildNumber = CatfishLocation + 1172 # 1172 because the OSVersionString pointer is 0x494 from the Catfish eyecatcher
		filename.seek(locationOfOSBuildNumber)
		dataOfOSBuildString = filename.read(4)
		pointerOfOSVersionString = struct.unpack("i", dataOfOSBuildString)[0]

		# Sanity Check 

		pointerLocationOfDarwinString = CatfishLocation + 28 # 28 as 0x201C Pointer to kernel version string
		filename.seek(pointerLocationOfDarwinString)
		dataOfDarwinStringPointer = filename.read(4)
		pointerOfDarwinString = struct.unpack("i", dataOfDarwinStringPointer)[0]
		#return the pointer for the Darwin Kernel version
		difference = (pointerOfDarwinString - locationOfDarwinString)
		
		filename.seek(pointerOfOSVersionString - difference, 0)
		getOSBuildNumberRead = filename.read(7) # null terminiated string so we can read 7 bytes.
		#print getOSBuildNumberRead
		return difference, getOSBuildNumberRead.replace('\x00', '')

def main():
	f = sys.argv[1]
	returnResult = imageInfo(f)
	difference, build = returnResult.catfishSearch(f)
	print "Difference:", difference
	print build
	if build == '10A432':
		print 'Suggested profile 10.6.0'
	elif build == '10D573' or build == '10D578':
		print 'Suggested profile 10.6.3'
	elif build == '10F659' or build == '10F616':
		print 'Suggested profile 10.6.4'
	elif build == '10H574' or build == '10H575':
		print 'Suggested profile 10.6.5'
	elif build == '10J567':
		print 'Suggested profile 10.6.6'
	elif build == '10J869' or build == '10J3250':
		print 'Suggested profile 10.6.7'
	elif build == '10K540' or build ==  '10K549':
		print 'Suggested profile 10.6.8'
	elif build == '11A511':
                print 'Suggeted profile 10.7.0'
	elif build == 'Darwin ':
		print 'Wrong Catfish symbol. Memory capture incomplete?'
	else:
		print 'Suggested profile not found'
	
	
if __name__ == "__main__":
   main()


