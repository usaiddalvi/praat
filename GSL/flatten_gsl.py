#!/usr/bin/python
#
# djmw 20080323
#
#  Makes the directory structure of gsl flat by renaming all files and references by #include
#  E.g. the file 'd/a.c' will be renamed as: gsl_d__a.c
# djmw 20100223 New makefile layout
#

import os, sys, glob, re, time, shutil

version = '1.10'
date = time.strftime('%Y%m%d')

gslconfigh = 'gsl__config.h'
fromdir = '/home/david/praat/gsl/gsl-' + version + '/'
todir = '/home/david/praat/gsl/GSL-' + version + '/'
log = open (todir + 'flatten_gsl' + version + '.log', 'w')
gslconfigh = 'gsl__config.h'

print >> log, date

dirs = ['blas', 'block', 'bspline', 'cblas', 'cdf', 'combination', 'complex', 'const',
	'deriv', 'dht', 'diff', 'doc', 'eigen', 'err', 'fft', 'fit', 'gsl', 'histogram', 'ieee-utils',
	'integration', 'linalg', 'matrix', 'min', 'monte', 'multifit', 'multimin',
	'multiroots', 'ntuple', 'ode-initval', 'permutation', 'poly', 'qrng', 'randist', 'rng', 'roots',
	'siman', 'sort', 'specfunc', 'statistics', 'sum', 'sys', 'vector', 'wavelet']

# left out: utils test
itype = 0
imake = 1
idist = 2
iname = 3
icount = 4
ihrep = 5
# per file: [type inmakefile indist renamed_as ntimesincluded headerreplacement]
# type = c h

def write_to_file (todir, basename, multilinetext):
	f = open (todir + basename, 'w')
	f.write (multilinetext)
	f.close()

def dict_from_list (dict, dir, list, type = 'c', inmake = 'y', indist = 'y'):
	for item in list:
		newname = 'gsl_' + dir + '__' + item
		if dir == 'gsl':
			newname = item
		dict[dir + '/' + item] = [type, inmake, indist, newname, 0 , '']

def get_all_files (dirs):
	files = {'./config.h': ['h', 'n', 'y', gslconfigh, 0, ''], \
		'./templates_on.h':['h', 'n', 'y', 'templates_on.h', 0, ''], \
		'./templates_off.h':['h', 'n', 'y', 'templates_off.h', 0, '']}
	for dir in dirs:
		os.chdir (fromdir + dir)
		dict_from_list (files, dir, glob.glob('*.c'), 'c', 'y')
		dict_from_list (files, dir, glob.glob('*.h'), 'h', 'n')
	return files

def quoted_include_get_newname (dict, key):
	if dict.has_key(key):
		dict[key][imake] = 'n'
		if dict[key][ihrep]:
			newname = dict[key][ihrep]
			dict['gsl/' + newname][icount] += 1
			print >> log, 'Corrected an include header error ' + key  + ' ' + newname
		else:
			newname = dict[key][iname]
			dict[key][icount] += 1
		return '"' + newname + '"'
	return None

# #include .....
# rewrite <gsl/file.h> to "file.h"
#         <file.h> -> <file.h>
#         "file.(c|h)" -> "gsl_dir__file.(c|h)"
def process_files (dict):
	include = re.compile (r'^(\s*\#\s*include\s+)([^\s]+)') # 2 groups
	delim = re.compile (r'(<|")\s*([^\s]+)\s*(>|")')
	for key, val in dict.items():
		(dir, base) = os.path.split (key)
		if dir == '.': # config.h will be/was done by hand, don't overwrite
			continue
		file_in_name = fromdir + key
		file_in = open (file_in_name, 'r')
		file_out_name = val[iname]
		output_lines = ''
		for line in file_in:
			minclude = include.search (line)
			if minclude:
				headerfile = minclude.group(2)
				mheader = delim.search (headerfile)
				header = mheader.group(2)
				if mheader.group(1) == '<':
					if header[0:4] == 'gsl/':
						newname = '"' + header[4:] +'"'
						dict[header][icount] += 1
					elif header == 'config.h':
						newname = '"' + gslconfigh + '"'
						dict['./'+header][icount] += 1
					else:
						newname = '<' + header + '>'
				else:
					newkey = dir + '/' + header
					newname = quoted_include_get_newname (dict, newkey)
					if not newname:
						newkey = './' + header
						newname = quoted_include_get_newname (dict, newkey)
						if not newname:
							newname = header
							print >> log, 'File does not exist: '+ header + ' From: ' + key
				output_lines += minclude.group(1) + newname + '\n'
			else:
				output_lines += line
		if val[idist] == 'y':
			write_to_file (todir, file_out_name, output_lines)
		else:
			dict[key][imake] = 'n'
	return dict

def gen_make_objects (dict, suffix, endofline):
	make_objects = ''
	(i , imax) = (0, 3)
	keysd = dict.keys()
	keysd.sort()
	for key in keysd:
		val = dict[key]
		if val[imake] == 'n':
			continue
		i += 1
		post = ' '
		if i%imax == 0: post = endofline
		(root, ext) = os.path.splitext (val[iname])
		make_objects += root + suffix + post
	return make_objects

def gen_sconscript(dict):
	make_objects = gen_make_objects (dict, '.c', ' \n   ')
	sconscript = '''# SConscript for library gsl. This file was generated by the program flatten_gsl.py
# djmw ''' + date + '''

sources = Split(""" ''' + make_objects + '''""")

Import ('env')
env.Library ('GSL', sources)

# End of SConscript
'''
	write_to_file (todir, 'SConscript', sconscript)

def gen_makefile (dict):
	make_objects = gen_make_objects (dict, '.o', ' \\\n   ')
	makefile = """# Makefile for library gsl. This file was generated by the program flatten_gsl.py
# djmw """ + date + """

include ../makefile.defs

CFLAGS = -I ../sys -I ../dwsys

OBJECTS = """ + make_objects + """

.PHONY: all clean

all: libgsl.a

clean:
	$(RM) $(OBJECTS)
	$(RM) libgsl.a

$(OBJECTS): *.h ../sys/*.h  ../dwsys/*.h

libgsl.a: $(OBJECTS)
	touch libgsl.a
	rm libgsl.a
	ar cq libgsl.a $(OBJECTS)
	$(RANLIB) libgsl.a

# end of Makefile
"""
	write_to_file (todir, 'Makefile', makefile)

def copy_file (fromdir, todir, file):
	text = open(fromdir + file).read()
	write_to_file (todir, file, text)

def preprocessing (current_gsl_version):
	if not os.path.exists (todir + gslconfigh):
		if not os.path.exists (fromdir + 'config.h'):
			sys.exit(todir + gslconfigh + ' and ' + fromdir + "config.h don't exist. Please run configure first!!")
		else:
			text = open(fromdir + 'config.h').read()
			write_to_file (todir, gslconfigh, text)
			print >> log, '----------- gsl__config.h created ------------------'
	copy_file (fromdir,todir, 'templates_on.h')
	copy_file (fromdir,todir, 'templates_off.h')
	print >> log, """
Post/Preprocesing
The layout of config.h/gsl__config.h varies from one version of gsl to the other
Do it by hand in """ + todir + """gsl__config.h:
Replace the #define "haves" with

#define HAVE_IEEEFP_H 0

#if defined(linux)
   #define HAVE_DECL_EXPM1 1
#else
   #define HAVE_DECL_EXPM1 0
#endif
#if defined(linux)
   #define HAVE_DECL_FINITE 1
#else
   #define HAVE_DECL_FINITE 0
#endif
#if defined(linux)
   #define HAVE_DECL_HYPOT 1
#else
   #define HAVE_DECL_HYPOT 0
#endif
#if defined(linux)
   #define HAVE_DECL_ISFINITE 0
#else
   #define HAVE_DECL_ISFINITE 0
#endif
#if defined(linux)
   #define HAVE_DECL_LOG1P 1
#else
   #define HAVE_DECL_LOG1P 0
#endif
#if defined(linux)
   #define HAVE_STRDUP 1
#else
   #define HAVE_STRDUP 0
#endif
#if defined(linux)
  #define HAVE_STRTOL 1
#else
  #define HAVE_STRTOL 0
#endif
#if defined(linux)
  #define HAVE_STRTOUL 1
#else
   #define HAVE_STRTOUL 0
#endif
#if defined(linux)
  #define HAVE_DLFCN_H 1
#else
   #define HAVE_DLFCN_H 0
#endif
#if defined(linux)
  #define HAVE_DECL_FEENABLEEXCEPT 1
#else
  #define HAVE_DECL_FEENABLEEXCEPT 0
#endif
# 3.Inlines:
#undef HAVE_INLINE
#ifdef sgi
  #define inline
#endif
#if defined(linux) || defined (macintosh) || defined (_WIN32)
  #define HAVE_DECL_ISINF 1
#else
  #define HAVE_DECL_ISINF 0
#endif
#if defined(linux) || defined (macintosh) || defined (_WIN32)
  #define HAVE_DECL_ISNAN 1
#else
  #define HAVE_DECL_ISNAN 0
#endif
# 4.
#if defined(linux)
  #define HAVE_GNUX86_IEEE_INTERFACE 1
#endif
 #undef HAVE_GNUSPARC_IEEE_INTERFACE
 #undef HAVE_GNUM68K_IEEE_INTERFACE
 #undef HAVE_GNUPPC_IEEE_INTERFACE
 #undef HAVE_SUNOS4_IEEE_INTERFACE
 #undef HAVE_SOLARIS_IEEE_INTERFACE
 #undef HAVE_HPUX11_IEEE_INTERFACE
 #undef HAVE_HPUX_IEEE_INTERFACE
 #undef HAVE_TRU64_IEEE_INTERFACE
 #undef HAVE_IRIX_IEEE_INTERFACE
 #undef HAVE_AIX_IEEE_INTERFACE
 #undef HAVE_FREEBSD_IEEE_INTERFACE
 #undef HAVE_OS2EMX_IEEE_INTERFACE
 #undef HAVE_NETBSD_IEEE_INTERFACE
 #undef HAVE_OPENBSD_IEEE_INTERFACE
 #undef HAVE_DARWIN_IEEE_INTERFACE
 #undef HAVE_DARWIN86_IEEE_INTERFACE

 #define GSL_DISABLE_DEPRECATED 1
 
#define USE_BLAS 0

By hand: Corrected in the fromdir/specfun/coupling.c:
#if ! defined (GSL_DISABLE_DEPRECATED)
  gsl_sf_coupling_6j_INCORRECT_e ....
#endif
#if ! defined (GSL_DISABLE_DEPRECATED)
  gsl_sf_coupling_6j_INCORRECT ....
#endif

"""

def post_processing (current_gsl_version):
	def correct_missing_prototypes (file, linenumber, prototype):
		f = open (file, 'r')
		lines = f.readlines ()
		lines.insert (linenumber, prototype + '\n')
		f.close ()
		f = open (file, 'w')
		f.writelines (lines)
		f.close ()
		print >> log, 'Inserted prototype in file '+ file
		print >> log, '    ' + prototype
	if current_gsl_version == '1.10':
		here = todir + '/'
		correct_missing_prototypes (here + 'gsl_matrix_complex_double.h', 235, \
			'int gsl_matrix_complex_isnonneg (const gsl_matrix_complex * m);')
		correct_missing_prototypes (here + 'gsl_matrix_complex_float.h', 235, \
			'int gsl_matrix_complex_float_isnonneg (const gsl_matrix_complex_float * m);')
		correct_missing_prototypes (here + 'gsl_matrix_complex_long_double.h', 235, \
			'int gsl_matrix_complex_long_double_isnonneg (const gsl_matrix_complex_long_double * m);')
		correct_missing_prototypes (here + 'gsl_vector_complex_double.h', 181, \
			'int gsl_vector_complex_isnonneg (const gsl_vector_complex * v);')
		correct_missing_prototypes (here + 'gsl_vector_complex_float.h', 181, \
			'int gsl_vector_complex_float_isnonneg (const gsl_vector_complex_float * v);')
		correct_missing_prototypes (here + 'gsl_vector_complex_long_double.h', 181, \
			'int gsl_vector_complex_long_double_isnonneg (const gsl_vector_complex_long_double * v);')

def remove_double_header_files (dict):
	num = 0
	for key,val in dict.items():
		(dir, base) = os.path.split (key)
		if dir == 'gsl': continue
		newkey = 'gsl/' + base
		if dict.has_key (newkey):
			f = open (fromdir + key, 'r')
			lines1 = f.read()
			f.close ()
			f = open (fromdir + newkey, 'r')
			lines2 = f.read()
			f.close ()
			if lines1 == lines2:
				num += 1
				dict[key][idist] = 'n'
				dict[key][ihrep] = base
				print >> log, 'Also in gsl/: ' + key
	return num

def exclude_test_files (dict):
	starts_with_test = re.compile (r'^test')
	for key in dict.keys ():
		(dir, base) = os.path.split (key)
		if starts_with_test.search (base):
			dict[key][idist] = 'n'
	dict['siman/siman_tsp.c'][idist] = 'n'

def print_file_selection (dict, type = 'c', inmake = 'n', indist = 'y'):
	selection = {}
	for key, val in dict.items():
		if val[itype] == type and val[imake] == inmake and val[idist] == indist:
			selection[key] = val[icount]
	keyss = selection.keys()
	keyss.sort()
	for key in keyss:
		print >> log, '%3d %s' % (selection[key], key)
	return len (keyss)

preprocessing (version)
files = get_all_files (dirs)
exclude_test_files (files)
print >> log, 'The following header files already exist in the gsl/ directory:'
ll = remove_double_header_files (files)
print >> log, 'Number of files = %d' % ll
print >> log, '\n\n process files'
process_files (files)
print >> log, '\n\n corect some header files:'
post_processing (version)
gen_sconscript (files)
gen_makefile (files)
print >> log, '\n\n header-files'
ll = print_file_selection (files, type = 'h')
print >> log, 'Number of files = %d' % ll
print >> log, '\n\n c-files'
ll = print_file_selection (files, type = 'c', inmake = 'y', indist = 'y')
print >> log, 'Number of files = %d' % ll
print >> log, '\n\n c-files included in other files'
ll = print_file_selection (files, type = 'c', inmake = 'n', indist = 'y')
print >> log, 'Number of files = %d' % ll
print >> log, '\n\n unused header-files'
ll = print_file_selection (files, type = 'h', indist = 'n')
print >> log, 'Number of files = %d' % ll
print >> log, '\n\n unused c-files'
ll = print_file_selection (files, type = 'c', indist = 'n')
print >> log, 'Number of files = %d' % ll


#print str(files)
