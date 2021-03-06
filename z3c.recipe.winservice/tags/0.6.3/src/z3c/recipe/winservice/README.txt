=====================
Z3 development recipe
=====================

z3c.recipe.winservice
---------------------

This Zope 3 recipes offers windows service installation support.

The 'service' recipe installes the required scripts and files whihc can be
used for install a windwos service.


Options
*******

The 'service' recipe accepts the following options:

name
  The windows service name option.

description
  The windows service description option.

runzope
  The script name which get used by the winservice. This script must exist in
  the bin folder and before we run this recipe exist. This script can get setup
  with the z3c.recipe.dev.app recipe.


Test
****

Lets define some (bogus) eggs that we can use in our application:

  >>> mkdir('demo1')
  >>> write('demo1', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo1')
  ... ''')

  >>> mkdir('demo2')
  >>> write('demo2', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo2', install_requires='demo1')
  ... ''')

We also need to setup an application. This is normaly done with the app recipe
defined in z3c.recipe.dev:

  >>> write('bin', 'app-script.py',
  ... '''
  ... dummy start script
  ... ''')


Now check if the setup was correct. This is true if we have already the
buildout files and our fake app-script.py installed:

  >>> ls('bin')
  -  app-script.py
  -  buildout-script.py
  -  buildout.exe

We'll create a `buildout.cfg` file that defines our winservice configuration:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = demo1 demo2
  ... parts = winservice
  ...
  ... [winservice]
  ... recipe = z3c.recipe.winservice:service
  ... name = Zope 3 Windows Service
  ... description = Zope 3 Windows Service description
  ... runzope = app
  ...
  ... ''' % globals())

Now, Let's run the buildout and see what we get:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/demo1'
  Develop: '/sample-buildout/demo2'
  Installing winservice.


The bin folder contains the windows service installer script:

  >>> ls('bin')
  -  app-script.py
  -  buildout-script.py
  -  buildout.exe
  -  winservice.py

The winservice.py contains the service setup for our zope windows service:

  >>> cat('bin', 'winservice.py')
  ##############################################################################
  #
  # Copyright (c) 2008 Zope Foundation and Contributors.
  # All Rights Reserved.
  #
  # This software is subject to the provisions of the Zope Public License,
  # Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  # THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  # WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  # WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  # FOR A PARTICULAR PURPOSE.
  #
  ##############################################################################
  """A Zope Windows NT service frontend.
  <BLANKLINE>
  Usage:
  <BLANKLINE>
    Installation
  <BLANKLINE>
      You can manually install, uninstall the service from the commandline.
  <BLANKLINE>
        python bin\winservice.py [options] install|update|remove|start [...]
             |stop|restart [...]|debug [...]
  <BLANKLINE>
      Options for 'install' and 'update' commands only:
  <BLANKLINE>
       --username domain\username : The Username the service is to run
                                    under
  <BLANKLINE>
       --password password : The password for the username
  <BLANKLINE>
       --startup [manual|auto|disabled] : How the service starts,
                                          default = manual
  <BLANKLINE>
      Commands
  <BLANKLINE>
        install : Installs the service
  <BLANKLINE>
        update : Updates the service, use this when you change
                 the service class implementation
  <BLANKLINE>
        remove : Removes the service
  <BLANKLINE>
        start : Starts the service, this can also be done from the
                services control panel
  <BLANKLINE>
        stop : Stops the service, this can also be done from the
               services control panel
  <BLANKLINE>
        restart : Restarts the service
  <BLANKLINE>
        debug : Runs the service in debug mode
  <BLANKLINE>
      You can view the usage options by running ntservice.py without any
      arguments.
  <BLANKLINE>
      Note: you may have to register the Python service program first,
  <BLANKLINE>
        win32\PythonService.exe /register
  <BLANKLINE>
    Starting Zope
  <BLANKLINE>
      Start Zope by clicking the 'start' button in the services control
      panel. You can set Zope to automatically start at boot time by
      choosing 'Auto' startup by clicking the 'statup' button.
  <BLANKLINE>
    Stopping Zope
  <BLANKLINE>
      Stop Zope by clicking the 'stop' button in the services control
      panel. You can also stop Zope through the web by going to the
      Zope control panel and by clicking 'Shutdown'.
  <BLANKLINE>
    Event logging
  <BLANKLINE>
      Zope events are logged to the NT application event log. Use the
      event viewer to keep track of Zope events.
  <BLANKLINE>
  """
  <BLANKLINE>
  import sys, os, time
  import pywintypes
  import win32serviceutil
  import win32service
  import win32event
  import win32process
  <BLANKLINE>
  # these are replacements from winservice recipe
  PYTHON = r'U:\Python24\python.exe'
  PYTHONDIR = os.path.split(PYTHON)[0]
  PYTHONSERVICE_EXE = r'%s\Lib\site-packages\win32\pythonservice.exe' % PYTHONDIR
  TOSTART = r'/sample-buildout/bin/app-script.py'
  SERVICE_NAME = '...sample_buildout_bin_app_script_py'
  SERVICE_DISPLAY_NAME = r'Zope 3 Windows Service'
  SERVICE_DESCRIPTION = r'Zope 3 Windows Service description'
  INSTANCE_HOME = os.path.dirname(os.path.dirname(TOSTART))
  <BLANKLINE>
  <BLANKLINE>
  # the max seconds we're allowed to spend backing off
  BACKOFF_MAX = 300
  # if the process runs successfully for more than BACKOFF_CLEAR_TIME
  # seconds, we reset the backoff stats to their initial values
  BACKOFF_CLEAR_TIME = 30
  # the initial backoff interval (the amount of time we wait to restart
  # a dead process)
  BACKOFF_INITIAL_INTERVAL = 5
  <BLANKLINE>
  <BLANKLINE>
  class NullOutput:
      """A stdout / stderr replacement that discards everything."""
  <BLANKLINE>
      def noop(self, *args, **kw):
          pass
  <BLANKLINE>
      write = writelines = close = seek = flush = truncate = noop
  <BLANKLINE>
      def __iter__(self):
          return self
  <BLANKLINE>
      def next(self):
          raise StopIteration
  <BLANKLINE>
      def isatty(self):
          return False
  <BLANKLINE>
      def tell(self):
          return 0
  <BLANKLINE>
      def read(self, *args, **kw):
          return ''
  <BLANKLINE>
      readline = read
  <BLANKLINE>
      def readlines(self, *args, **kw):
          return []
  <BLANKLINE>
  <BLANKLINE>
  class Zope3Service(win32serviceutil.ServiceFramework):
      """ A class representing a Windows NT service that can manage an
      instance-home-based Zope/ZEO/ZRS processes """
  <BLANKLINE>
      # The PythonService model requires that an actual on-disk class declaration
      # represent a single service.  Thus, the below definition of start_cmd,
      # must be overridden in a subclass in a file within the instance home for
      # each instance.  The below-defined start_cmd (and _svc_display_name_
      # and _svc_name_) are just examples.
  <BLANKLINE>
      _svc_name_ = SERVICE_NAME
      _svc_display_name_ = SERVICE_DISPLAY_NAME
      _svc_description_ = SERVICE_DESCRIPTION
  <BLANKLINE>
      _exe_name_ = PYTHONSERVICE_EXE
      start_cmd = ''
  <BLANKLINE>
      def __init__(self, args):
          if not os.path.exists(PYTHON):
              raise OSError("%s does not exist" % PYTHON)
          if not os.path.exists(TOSTART):
              raise OSError("%s does not exist" % TOSTART)
  <BLANKLINE>
          self.start_cmd = '"%s" "%s"' % (PYTHON, TOSTART)
  <BLANKLINE>
          win32serviceutil.ServiceFramework.__init__(self, args)
          # Create an event which we will use to wait on.
          # The "service stop" request will set this event.
          self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
          self.redirectOutput()
  <BLANKLINE>
      def redirectOutput(self):
          sys.stdout.close()
          sys.stderr.close()
          sys.stdout = NullOutput()
          sys.stderr = NullOutput()
  <BLANKLINE>
      def SvcStop(self):
          # Before we do anything, tell the SCM we are starting the stop process.
          self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
  <BLANKLINE>
          # TODO:  This TerminateProcess call doesn't make much sense:  it's
          # doing a hard kill _first_, never giving the process a chance to
          # shut down cleanly.  Compare to current Zope2 service code, which
          # uses Windows events to give the process a chance to shut down
          # cleanly, doing a hard kill only if that doesn't succeed.
  <BLANKLINE>
          # stop the process if necessary
          try:
              win32process.TerminateProcess(self.hZope, 0)
          except pywintypes.error:
              # the process may already have been terminated
              pass
          # And set my event.
          win32event.SetEvent(self.hWaitStop)
  <BLANKLINE>
      # SvcStop only gets triggered when the user explictly stops (or restarts)
      # the service.  To shut the service down cleanly when Windows is shutting
      # down, we also need to hook SvcShutdown.
      SvcShutdown = SvcStop
  <BLANKLINE>
      def createProcess(self, cmd):
          #need to set current dir to INSTANCE_HOME otherwise pkg_resources will
          #be pissed (in a combination with paster)
          return win32process.CreateProcess(
              None, cmd, None, None, 0, 0, None,
              INSTANCE_HOME,
              win32process.STARTUPINFO())
  <BLANKLINE>
      def SvcDoRun(self):
          # indicate to Zope that the process is daemon managed (restartable)
          os.environ['ZMANAGED'] = '1'
  <BLANKLINE>
          # daemon behavior:  we want to to restart the process if it
          # dies, but if it dies too many times, we need to give up.
  <BLANKLINE>
          # we use a simple backoff algorithm to determine whether
          # we should try to restart a dead process:  for each
          # time the process dies unexpectedly, we wait some number of
          # seconds to restart it, as determined by the backoff interval,
          # which doubles each time the process dies.  if we exceed
          # BACKOFF_MAX seconds in cumulative backoff time, we give up.
          # at any time if we successfully run the process for more thab
          # BACKOFF_CLEAR_TIME seconds, the backoff stats are reset.
  <BLANKLINE>
          # the initial number of seconds between process start attempts
          backoff_interval = BACKOFF_INITIAL_INTERVAL
          # the cumulative backoff seconds counter
          backoff_cumulative = 0
  <BLANKLINE>
          import servicemanager
  <BLANKLINE>
          # log a service started message
          servicemanager.LogMsg(
              servicemanager.EVENTLOG_INFORMATION_TYPE,
              servicemanager.PYS_SERVICE_STARTED,
              (self._svc_name_, ' (%s)' % self._svc_display_name_))
  <BLANKLINE>
          while 1:
              start_time = time.time()
              info = self.createProcess(self.start_cmd)
              self.hZope = info[0] # the pid
              if backoff_interval > BACKOFF_INITIAL_INTERVAL:
                  # if we're in a backoff state, log a message about
                  # starting a new process
                  servicemanager.LogInfoMsg(
                      '%s (%s): recovering from died process, new process '
                      'started' % (self._svc_name_, self._svc_display_name_)
                      )
              rc = win32event.WaitForMultipleObjects(
                  (self.hWaitStop, self.hZope), 0, win32event.INFINITE)
              if rc == win32event.WAIT_OBJECT_0:
                  # user sent a stop service request
                  self.SvcStop()
                  break
              else:
                  # user did not send a service stop request, but
                  # the process died; this may be an error condition
                  status = win32process.GetExitCodeProcess(self.hZope)
                  if status == 0:
                      # the user shut the process down from the web
                      # interface (or it otherwise exited cleanly)
                      break
                  else:
                      # this was an abormal shutdown.  if we can, we want to
                      # restart the process but if it seems hopeless,
                      # don't restart an infinite number of times.
                      if backoff_cumulative > BACKOFF_MAX:
                          # it's hopeless
                          servicemanager.LogErrorMsg(
                            '%s (%s): process could not be restarted due to max '
                            'restart attempts exceeded' % (
                              self._svc_display_name_, self._svc_name_
                            ))
                          self.SvcStop()
                          break
                      servicemanager.LogWarningMsg(
                         '%s (%s): process died unexpectedly.  Will attempt '
                         'restart after %s seconds.' % (
                              self._svc_name_, self._svc_display_name_,
                              backoff_interval
                              )
                         )
                      # if BACKOFF_CLEAR_TIME seconds have elapsed since we last
                      # started the process, reset the backoff interval
                      # and the cumulative backoff time to their original
                      # states
                      if time.time() - start_time > BACKOFF_CLEAR_TIME:
                          backoff_interval = BACKOFF_INITIAL_INTERVAL
                          backoff_cumulative = 0
                      # we sleep for the backoff interval.  since this is async
                      # code, it would be better done by sending and
                      # catching a timed event (a service
                      # stop request will need to wait for us to stop sleeping),
                      # but this works well enough for me.
                      time.sleep(backoff_interval)
                      # update backoff_cumulative with the time we spent
                      # backing off.
                      backoff_cumulative = backoff_cumulative + backoff_interval
                      # bump the backoff interval up by 2* the last interval
                      backoff_interval = backoff_interval * 2
  <BLANKLINE>
                      # loop and try to restart the process
  <BLANKLINE>
          # log a service stopped message
          servicemanager.LogMsg(
              servicemanager.EVENTLOG_INFORMATION_TYPE,
              servicemanager.PYS_SERVICE_STOPPED,
              (self._svc_name_, ' (%s) ' % self._svc_display_name_))
  <BLANKLINE>
  <BLANKLINE>
  if __name__ == '__main__':
      import win32serviceutil
      if os.path.exists(PYTHONSERVICE_EXE):
          # This ensures that pythonservice.exe is registered...
          os.system('"%s" -register' % PYTHONSERVICE_EXE)
      win32serviceutil.HandleCommandLine(Zope3Service)



Debug
-----

This option is for service scripts having fundamental problems.
The problem with those scripts is that they are starting and stopping at once.
Seemingly there is no output, no sing that the script did something.
And because they run in a subprocess until those scripts have logging established
they won't have any chance to report the error.
For this we'll setup a bare catch-all around the whole script and log any
exceptions to the windows event log.
CAUTION: this takes a copy of the app-script.py but does not update the patched
result when it changes!

We can enable the ``debug`` option:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = demo1 demo2
  ... parts = winservice
  ...
  ... [winservice]
  ... recipe = z3c.recipe.winservice:service
  ... name = Zope 3 Windows Service
  ... description = Zope 3 Windows Service description
  ... runzope = app
  ... debug = true
  ...
  ... ''' % globals())

Now, Let's run the buildout and see what we get:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/demo1'
  Develop: '/sample-buildout/demo2'
  Uninstalling winservice.
  Installing winservice.


The bin folder contains the windows service installer script:

  >>> ls('bin')
  -  app-script.py
  -  app-servicedebug.py
  -  buildout-script.py
  -  buildout.exe
  -  winservice.py

The winservice.py file gets changed according to the new script name:

  >>> cat('bin', 'winservice.py')
  ##############################################################################
  ...TOSTART = r'/sample-buildout/bin/app-servicedebug.py'...
  ...SERVICE_NAME = '...bin_app_script_py'...

The debug script contains a bare catch-all and a logger:

  >>> cat('bin', 'app-servicedebug.py')
  <BLANKLINE>
  def exceptionlogger():
      import servicemanager
      import traceback
      servicemanager.LogErrorMsg("Script %s had an exception: %s" % (
        __file__, traceback.format_exc()
      ))
  <BLANKLINE>
  try:
  <BLANKLINE>
      dummy start script
  <BLANKLINE>
  except Exception, e:
      exceptionlogger()
