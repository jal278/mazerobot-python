# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.11
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_mazepy', [dirname(__file__)])
        except ImportError:
            import _mazepy
            return _mazepy
        if fp is not None:
            try:
                _mod = imp.load_module('_mazepy', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _mazepy = swig_import_helper()
    del swig_import_helper
else:
    import _mazepy
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


class floatArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, floatArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, floatArray, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _mazepy.new_floatArray(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _mazepy.delete_floatArray
    __del__ = lambda self : None;
    def __getitem__(self, *args): return _mazepy.floatArray___getitem__(self, *args)
    def __setitem__(self, *args): return _mazepy.floatArray___setitem__(self, *args)
    def cast(self): return _mazepy.floatArray_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _mazepy.floatArray_frompointer
    if _newclass:frompointer = staticmethod(_mazepy.floatArray_frompointer)
floatArray_swigregister = _mazepy.floatArray_swigregister
floatArray_swigregister(floatArray)

def floatArray_frompointer(*args):
  return _mazepy.floatArray_frompointer(*args)
floatArray_frompointer = _mazepy.floatArray_frompointer

class feature_detector(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, feature_detector, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, feature_detector, name)
    __repr__ = _swig_repr
    __swig_getmethods__["end_goal"] = lambda x: _mazepy.feature_detector_end_goal
    if _newclass:end_goal = staticmethod(_mazepy.feature_detector_end_goal)
    __swig_getmethods__["start_dist"] = lambda x: _mazepy.feature_detector_start_dist
    if _newclass:start_dist = staticmethod(_mazepy.feature_detector_start_dist)
    __swig_getmethods__["closest_goal"] = lambda x: _mazepy.feature_detector_closest_goal
    if _newclass:closest_goal = staticmethod(_mazepy.feature_detector_closest_goal)
    __swig_getmethods__["endx"] = lambda x: _mazepy.feature_detector_endx
    if _newclass:endx = staticmethod(_mazepy.feature_detector_endx)
    __swig_getmethods__["endy"] = lambda x: _mazepy.feature_detector_endy
    if _newclass:endy = staticmethod(_mazepy.feature_detector_endy)
    __swig_getmethods__["midx"] = lambda x: _mazepy.feature_detector_midx
    if _newclass:midx = staticmethod(_mazepy.feature_detector_midx)
    __swig_getmethods__["midy"] = lambda x: _mazepy.feature_detector_midy
    if _newclass:midy = staticmethod(_mazepy.feature_detector_midy)
    __swig_getmethods__["spd"] = lambda x: _mazepy.feature_detector_spd
    if _newclass:spd = staticmethod(_mazepy.feature_detector_spd)
    __swig_getmethods__["coll"] = lambda x: _mazepy.feature_detector_coll
    if _newclass:coll = staticmethod(_mazepy.feature_detector_coll)
    __swig_getmethods__["turn"] = lambda x: _mazepy.feature_detector_turn
    if _newclass:turn = staticmethod(_mazepy.feature_detector_turn)
    __swig_getmethods__["state_entropy"] = lambda x: _mazepy.feature_detector_state_entropy
    if _newclass:state_entropy = staticmethod(_mazepy.feature_detector_state_entropy)
    def __init__(self): 
        this = _mazepy.new_feature_detector()
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _mazepy.delete_feature_detector
    __del__ = lambda self : None;
feature_detector_swigregister = _mazepy.feature_detector_swigregister
feature_detector_swigregister(feature_detector)

def feature_detector_end_goal(*args):
  return _mazepy.feature_detector_end_goal(*args)
feature_detector_end_goal = _mazepy.feature_detector_end_goal

def feature_detector_start_dist(*args):
  return _mazepy.feature_detector_start_dist(*args)
feature_detector_start_dist = _mazepy.feature_detector_start_dist

def feature_detector_closest_goal(*args):
  return _mazepy.feature_detector_closest_goal(*args)
feature_detector_closest_goal = _mazepy.feature_detector_closest_goal

def feature_detector_endx(*args):
  return _mazepy.feature_detector_endx(*args)
feature_detector_endx = _mazepy.feature_detector_endx

def feature_detector_endy(*args):
  return _mazepy.feature_detector_endy(*args)
feature_detector_endy = _mazepy.feature_detector_endy

def feature_detector_midx(*args):
  return _mazepy.feature_detector_midx(*args)
feature_detector_midx = _mazepy.feature_detector_midx

def feature_detector_midy(*args):
  return _mazepy.feature_detector_midy(*args)
feature_detector_midy = _mazepy.feature_detector_midy

def feature_detector_spd(*args):
  return _mazepy.feature_detector_spd(*args)
feature_detector_spd = _mazepy.feature_detector_spd

def feature_detector_coll(*args):
  return _mazepy.feature_detector_coll(*args)
feature_detector_coll = _mazepy.feature_detector_coll

def feature_detector_turn(*args):
  return _mazepy.feature_detector_turn(*args)
feature_detector_turn = _mazepy.feature_detector_turn

def feature_detector_state_entropy(*args):
  return _mazepy.feature_detector_state_entropy(*args)
feature_detector_state_entropy = _mazepy.feature_detector_state_entropy

class mazenav(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, mazenav, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, mazenav, name)
    __repr__ = _swig_repr
    def make_random(self): return _mazepy.mazenav_make_random(self)
    __swig_getmethods__["seed"] = lambda x: _mazepy.mazenav_seed
    if _newclass:seed = staticmethod(_mazepy.mazenav_seed)
    __swig_getmethods__["random_seed"] = lambda x: _mazepy.mazenav_random_seed
    if _newclass:random_seed = staticmethod(_mazepy.mazenav_random_seed)
    def __init__(self): 
        this = _mazepy.new_mazenav()
        try: self.this.append(this)
        except: self.this = this
    def copy(self): return _mazepy.mazenav_copy(self)
    def complexity(self): return _mazepy.mazenav_complexity(self)
    def map(self): return _mazepy.mazenav_map(self)
    __swig_getmethods__["initmaze"] = lambda x: _mazepy.mazenav_initmaze
    if _newclass:initmaze = staticmethod(_mazepy.mazenav_initmaze)
    def mutate(self): return _mazepy.mazenav_mutate(self)
    def isvalid(self): return _mazepy.mazenav_isvalid(self)
    def clear(self): return _mazepy.mazenav_clear(self)
    def distance(self, *args): return _mazepy.mazenav_distance(self, *args)
    def init_rand(self): return _mazepy.mazenav_init_rand(self)
    def save(self, *args): return _mazepy.mazenav_save(self, *args)
    def load_new(self, *args): return _mazepy.mazenav_load_new(self, *args)
    def get_x(self): return _mazepy.mazenav_get_x(self)
    def get_y(self): return _mazepy.mazenav_get_y(self)
    def viable(self): return _mazepy.mazenav_viable(self)
    def solution(self): return _mazepy.mazenav_solution(self)
    __swig_destroy__ = _mazepy.delete_mazenav
    __del__ = lambda self : None;
mazenav_swigregister = _mazepy.mazenav_swigregister
mazenav_swigregister(mazenav)

def mazenav_seed(*args):
  return _mazepy.mazenav_seed(*args)
mazenav_seed = _mazepy.mazenav_seed

def mazenav_random_seed():
  return _mazepy.mazenav_random_seed()
mazenav_random_seed = _mazepy.mazenav_random_seed

def mazenav_initmaze(*args):
  return _mazepy.mazenav_initmaze(*args)
mazenav_initmaze = _mazepy.mazenav_initmaze

# This file is compatible with both classic and new-style classes.


