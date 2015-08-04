*ccl_bplist is a small Python module for dealing with binary property lists (bplists). It also contains special helper functionality to simplify the processing of NSKeyedArchiver structures often found in binary property lists.*

It converts the binary property list file contents into a native Python object.

Property List Type | Returned Python Type
------------------ | --------------------
null | None
true | True
false | False
integer | int
real | float
uid | int
date | datetime.datetime
string | str
data | bytes
array | list
dict | dict
set | list

----

# Quick-Start

Here's a quick overview of the module's features:

## Opening Property Lists

At its most basic, just import the module, create a file-like object around your plist (here I'm opening a file, but often I find that I'm dealing with embedded plists, in which case `io.BytesIO` is very useful).
```python
>>> import ccl_bplist
>>> f = open("plist.plist", "rb")
>>> plist = ccl_bplist.load(f)
>>> 
>>> plist
{'$objects': ['$null', {'apiKey': UID: 10, 'eventLog': UID: 7, 'locale': UID: 12, '$class': UID: 14, 'pauseTime': UID: 4, 'totalErrorCount': 0, 'internetAvailable': True, 'errors': UID: 9, 'userID': UID: 0, 'appVersion': UID: 11, 'latitude': 0.0, 'eventCounts': UID: 5, 'eventLogComplete': True, 'crashed': False, 'pageViewCount': 0, 'startTime': UID: 2, 'pauseIntervalMillis': 0, 'gender': -1, 'longitude': 0.0, 'serializationVersion': 1, 'timeZone': UID: 13, 'accuracy': 0.0}, {'$class': UID: 3, 'NS.time': 378032076.116256}, {'$classes': ['NSDate', 'NSObject'], '$classname': 'NSDate'}, {'$class': UID: 3, 'NS.time': 378032077.674404}, {'$class': UID: 6, 'NS.keys': [], 'NS.objects': []}, {'$classes': ['NSMutableDictionary', 'NSDictionary', 'NSObject'], '$classname': 'NSMutableDictionary'}, {'$class': UID: 8, 'NS.objects': []}, {'$classes': ['NSMutableArray', 'NSArray', 'NSObject'], '$classname': 'NSMutableArray'}, {'$class': UID: 8, 'NS.objects': []}, 'BMPNB5HT2H63KM42BB83', '4.0.1', 'en_GB', 'Europe/London', {'$classes': ['FlurrySession', 'NSObject'], '$classname': 'FlurrySession'}], '$top': {'root': UID: 1}, '$version': 100000, '$archiver': 'NSKeyedArchiver'}
```

The plist is converted to a native Python object (the translations of plist data-type to Python data-types are listed above). 

## Working with NSKeyedArchiver Files

In this case the plist is one that has been created by Apple's NSKeyedArchiver class which means it's not a whole lot of fun to work with. Luckily, ccl_bplist can deserialise the object and give you the actual structure of the data.

```python
>>> ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist)
>>> ns_keyed_archiver_obj
{'apiKey': UID: 10, 'eventLog': UID: 7, 'locale': UID: 12, '$class': UID: 14, 'eventLogComplete': True, 'crashed': False, 'pageViewCount': 0, 'startTime': UID: 2, 'pauseTime': UID: 4, 'totalErrorCount': 0, 'internetAvailable': True, 'errors': UID: 9, 'pauseIntervalMillis': 0, 'gender': -1, 'userID': UID: 0, 'appVersion': UID: 11, 'longitude': 0.0, 'serializationVersion': 1, 'latitude': 0.0, 'timeZone': UID: 13, 'accuracy': 0.0, 'eventCounts': UID: 5}
```

The module assumes that if the top-level dictionary structure is `$top/root` that the object that you want returning sits beneath `top`. You can override this behaviour is you prefer:

```python
>>> ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
>>> ns_keyed_archiver_obj
{'root': UID: 1}
```

You'll notice in both of these cases that we have `UID` objects. This is because NSKeyedArchiver maintains an object-table, and in the structure the objects are referred by their position in the object-table (more details here: http://www.cclgroupltd.com/digital-forensics/rd/geek-post-nskeyedarchiver-files-%E2%80%93-what-are-they-and-how-can-i-use-them.html. The module doesn't look-up the objects until they are requested, both for speed and (mostly) because you can have infinitely recursing structures. If you access a UID object in a list or dictionary it will be looked up and returned:

```python
>>> ns_keyed_archiver_obj["root"]
{'apiKey': UID: 10, 'eventLog': UID: 7, 'locale': UID: 12, '$class': UID: 14, 'eventLogComplete': True, 'crashed': False, 'pageViewCount': 0, 'startTime': UID: 2, 'pauseTime': UID: 4, 'totalErrorCount': 0, 'internetAvailable': True, 'errors': UID: 9, 'pauseIntervalMillis': 0, 'gender': -1, 'userID': UID: 0, 'appVersion': UID: 11, 'longitude': 0.0, 'serializationVersion': 1, 'latitude': 0.0, 'timeZone': UID: 13, 'accuracy': 0.0, 'eventCounts': UID: 5}
```

## Automatic Conversion of Common NSObjects

NSKeyed Archiver contains serialisations of ObjectiveC objects which would usually require extra code to deal with, but in version 0.13 of the module we've added a set of convenience features to make dealing with these data types a lot simpler.

```python
>>> ns_keyed_archiver_obj["root"]["eventLog"]
{'$class': UID: 8, 'NS.objects': []}
```

Here we've accessed an object in this plist, we can inspect the type of the object by looking at the "$class" key:

```python
>>> ns_keyed_archiver_obj["root"]["eventLog"]["$class"]
{'$classes': ['NSMutableArray', 'NSArray', 'NSObject'], '$classname': 'NSMutableArray'}
```

We can see that this is a serialisation of an `NSMutableArray`. We could access the contents of the array in the `NS.objects` key (which in this case contains an empty list), alternatively we can set a converter function for the module to use, you can write your own, but the module comes with one built in which you can enable like this:

```python
>>> ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
```

(NB this enables the converter module-wide, not just for objects that you're currently working on)

If we access the same object now, it automatically gets converted into a nice, native Python list:

```python
>>> ns_keyed_archiver_obj["root"]["eventLog"]
[]
```

If you want to turn this functionality off, just set the converter function to a pass-through function:

```python
>>> ccl_bplist.set_object_converter(lambda x: x)
```

This built-in converter also works for NSDictionary:

```python
>>> ns_keyed_archiver_obj["root"]["eventCounts"]
{'$class': UID: 6, 'NS.keys': [], 'NS.objects': []}

>>> ns_keyed_archiver_obj["root"]["eventCounts"]["$class"]
{'$classes': ['NSMutableDictionary', 'NSDictionary', 'NSObject'], '$classname': 'NSMutableDictionary'}

>>> ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
>>> ns_keyed_archiver_obj["root"]["eventCounts"]
{}

>>> ccl_bplist.set_object_converter(lambda x: x)
```

NSDate:

```python
>>> ns_keyed_archiver_obj["root"]["startTime"]
{'$class': UID: 3, 'NS.time': 378032076.116256}

>>> ns_keyed_archiver_obj["root"]["startTime"]["$class"]
{'$classes': ['NSDate', 'NSObject'], '$classname': 'NSDate'}

>>> ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
>>> ns_keyed_archiver_obj["root"]["startTime"]
datetime.datetime(2012, 12, 24, 8, 54, 36, 116256)

>>> ccl_bplist.set_object_converter(lambda x: x)
```

and the way that NSKeyedArchiver serialises Null as a string containing "$null":

```python
>>> ns_keyed_archiver_obj["root"]["userID"]
'$null'

>>> ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
>>> print(ns_keyed_archiver_obj["root"]["userID"])
None

```
