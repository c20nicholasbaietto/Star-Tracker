%module beast
%{
#include "config.h"
#include "stars.h"
#include "constellations.h"
#include "beast.h"
%}
%typemap(out) float * {
	int i;
	$result = PyList_New(3);
	for (i = 0; i < 3; i++) {
		PyObject *o = PyFloat_FromDouble((double) $1[i]);
		PyList_SetItem($result,i,o);
	}
}
//newobject gives python control of these objects
%newobject star_db::copy;
%newobject star_db::copy_n_brightest;
%newobject star_db::search;
%newobject star_db::operator-;
%newobject star_db::operator&;
%newobject star_query::from_kdmask;
%newobject star_query::from_kdresults;
%newobject match_result::from_match;
%include "config.h"
%include "stars.h"
%include "constellations.h"
%include "beast.h"
