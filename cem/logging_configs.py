# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\logging_configs.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os, textwrap

class CEMTimedRotatingFileHandler(TimedRotatingFileHandler):
    __doc__ = "\n    Custom TimedRotatingFileHandler that supports adding the serial number to the log filename after initialisation\n    See #71 for discussion.\n    "

    def add_sn_to_filename(self, serial_number):
        """
        Method to add the serial number to the log file. This results in the current logfile being closed, renamed and re-opened
        """
        self.stream.close()
        original_basename = self.baseFilename
        try:
            prefix, filetype = original_basename.rsplit(".", maxsplit=1)
            self.baseFilename = f"{prefix}_{serial_number}.{filetype}"
        except ValueError:
            self.baseFilename = f"{original_basename}_{serial_number}"
        else:
            if os.path.exists(self.baseFilename):
                os.remove(self.baseFilename)
            os.rename(original_basename, self.baseFilename)
            if not self.delay:
                self.stream = self._open()


class TabIndentedExceptionsFormatter(logging.Formatter):
    __doc__ = "\n    Minor override of logging.Formatter which tab indents exceptions so that they are more readable\n    See https://gitlab.com/moglabs/software/external/cem-app/-/issues/132 for details.\n    "

    def formatException(self, exc_info):
        """
        format override for exceptions. Uses parent implementation and then simply indents lines with tab.
        """
        return textwrap.indent(super().formatException(exc_info), "\t", lambda line: True)


CEM_CONFIG_PRODUCTION = {'version':1, 
 'disable_existing_loggers':False, 
 'formatters':{"standard": {'()':TabIndentedExceptionsFormatter, 
               'format':"%(asctime)s %(name)s:%(levelname)s:%(message)s", 
               'datefmt':"%d-%m-%Y %H:%M:%S"}}, 
 'handlers':{"timed_rotating_file": {
                          '()': CEMTimedRotatingFileHandler, 
                          'level': 'NOTSET', 
                          'formatter': 'standard', 
                          'filename': 'moglabs_cem.log', 
                          'when': 'D', 
                          'backupCount': 7}}, 
 'loggers':{"": {'handlers':[
        "timed_rotating_file"], 
       'level':"WARNING"}}}
CEM_CONFIG_INTERNAL = {'version':1, 
 'disable_existing_loggers':False, 
 'formatters':{'standard':{'()':TabIndentedExceptionsFormatter, 
   'format':"%(asctime)s %(name)s:%(levelname)s:%(message)s", 
   'datefmt':"%d-%m-%Y %H:%M:%S"}, 
  'short':{'()':TabIndentedExceptionsFormatter, 
   'format':"%(name)s:%(levelname)s:%(message)s"}}, 
 'handlers':{'console':{
   'level': 'NOTSET', 
   'formatter': 'short', 
   'class': 'logging.StreamHandler', 
   'stream': 'ext://sys.stdout'}, 
  'file':{
   'level': 'NOTSET', 
   'formatter': 'standard', 
   'class': 'logging.handlers.RotatingFileHandler', 
   'filename': 'cem_mogdebug.log', 
   'mode': 'a', 
   'maxBytes': 1048576, 
   'backupCount': 1}}, 
 'loggers':{'':{'handlers':[
    "console", "file"], 
   'level':"DEBUG"}, 
  'mogui':{'handlers':[
    "console", "file"], 
   'level':"INFO"}, 
  'pyvisa':{'handlers':[
    "console", "file"], 
   'level':"INFO"}}}

# okay decompiling cem/logging_configs.pyc
