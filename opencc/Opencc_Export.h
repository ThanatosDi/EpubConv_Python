
#ifndef OPENCC_EXPORT_H
#define OPENCC_EXPORT_H

#ifdef Opencc_BUILT_AS_STATIC
#  define OPENCC_EXPORT
#  define OPENCC_NO_EXPORT
#else
#  ifndef OPENCC_EXPORT
#    ifdef libopencc_EXPORTS
        /* We are building this library */
#      define OPENCC_EXPORT __declspec(dllexport)
#    else
        /* We are using this library */
#      define OPENCC_EXPORT __declspec(dllimport)
#    endif
#  endif

#  ifndef OPENCC_NO_EXPORT
#    define OPENCC_NO_EXPORT 
#  endif
#endif

#ifndef OPENCC_DEPRECATED
#  define OPENCC_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef OPENCC_DEPRECATED_EXPORT
#  define OPENCC_DEPRECATED_EXPORT OPENCC_EXPORT OPENCC_DEPRECATED
#endif

#ifndef OPENCC_DEPRECATED_NO_EXPORT
#  define OPENCC_DEPRECATED_NO_EXPORT OPENCC_NO_EXPORT OPENCC_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef OPENCC_NO_DEPRECATED
#    define OPENCC_NO_DEPRECATED
#  endif
#endif

#endif
