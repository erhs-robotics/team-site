#! /usr/bin/python

from optparse import OptionParser
import re

parser = OptionParser()
parser.add_option("-M", "--major", action="store_true", dest="major", help="bumps a.b.c to (a+1).0.0")
parser.add_option("-m", "--minor", action="store_true", dest="minor", help="bumps a.b.c to a.(b+1).0")
parser.add_option("-f", "--bugfix", action="store_true", dest="bugfix", help="bumps a.b.c to a.b.(c+1)")
parser.add_option("-s", "--show", action="store_true", dest="show", help="show current version")
parser.add_option("-v", dest="version", help="specifies a version")

(options, args) = parser.parse_args()

f = open("app.yaml", "r+w")
text = f.read()

m = re.search("version:( +)(\d+)-(\d+)-(\d+)", text)
major = int(m.group(2))
minor = int(m.group(3))
revision = int(m.group(4))
if options.show:
	print "current version: %s-%s-%s" % (major, minor, revision)
	exit()

if options.version:
	if re.match("(\d+)-(\d+)-(\d+)$", options.version):
		version = options.version.split('-')
		major = int(version[0])
		minor = int(version[1])
		revision = int(version[2])
	else:
		print "version format incorrect!"
		parser.print_help()
		exit()

if options.major:
	major += 1
	minor = 0
	revision = 0

if options.minor:
	minor += 1
	revision = 0

if options.bugfix:
	revision += 1

text = text.replace(m.group(0), "version: %s-%s-%s" % (major, minor, revision))

f.seek(0)
f.write(text)
f.truncate()
f.close()

print "new version: %s-%s-%s" % (major, minor, revision)
		



