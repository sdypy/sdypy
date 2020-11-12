==============
Scope of SDyPy
==============

Here, we describe the scope of the SDyPy project. The aim of this project is to defragment 
the open source scientific effort in the field of structural dynamics research. There are several
packages available that support different aspects of structural dynamics and this project should
help in defining good practice / common tools which would help those packages to work (better) 
with each other.


In particular, the goals are:

- **Define the prefered data APIs**

  - By defining prefered array data structures
  - By defining prefered dataframe data structures
  - By extending the Style Guide for Python Code (PEP8) to parameter names in SDyPy
  - By defining parameter names prefered in SDyPy

- **Provide standard data-sets for testing**

  - SDyPy should include general datasets (e.g. SIMO, MIMO) for testing of different scientific methods.
  
- **Package dependency**

  - SDyPy code should preferably be pure Python
  - The dependency on packages `numpy`, `scipy`, `matplotlib` is encouraged
  - The dependency on structural dynamics packages which adhere to the SDyPy project is ecouraged

- **Unification of data visualisation** 
  
  - SDyPy or related packages should provide and easy way for generation 
    of publication ready and interactive visualisation for:
      - models (nodes, sufraces, elements, STL),
      - measurement location,
      - mode shapes,...