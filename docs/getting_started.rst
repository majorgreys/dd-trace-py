.. include:: ./shared.rst


.. _Getting_Started:

Getting Started
===============

.. _ddtracerun:

``ddtrace-run``
---------------

Automatic setup is accomplished by using the ``ddtrace-run`` command as a
wrapper for your python entry-point.

For example if you start your application with ``python app.py`` then run::

    ddtrace-run python app.py

For more advanced usage of ``ddtrace-run`` refer to the documentation :ref:`here<ddtracerun>`.


If ``ddtrace-run`` isn't suitable for your application then :ref:`patch_all` can be used::

    import ddtrace

    ddtrace.patch_all()


``ddtrace-run`` will trace :ref:`supported<Supported Libraries>` web frameworks
and database modules without the need for changing your code::

  $ ddtrace-run -h

  Execute the given Python program, after configuring it
  to emit Datadog traces.

  Append command line arguments to your program as usual.

  Usage: ddtrace-run <my_program>


The environment variables for ``ddtrace-run`` used to configure the tracer are
detailed in :ref:`Configuration`.

``ddtrace-run`` respects a variety of common entrypoints for web applications:

- ``ddtrace-run python my_app.py``
- ``ddtrace-run python manage.py runserver``
- ``ddtrace-run gunicorn myapp.wsgi:application``


Pass along command-line arguments as your program would normally expect them::

$ ddtrace-run gunicorn myapp.wsgi:application --max-requests 1000 --statsd-host localhost:8125

If you're running in a Kubernetes cluster and still don't see your traces, make
sure your application has a route to the tracing Agent. An easy way to test
this is with a::

$ pip install ipython
$ DATADOG_TRACE_DEBUG=true ddtrace-run ipython

Because iPython uses SQLite, it will be automatically instrumented and your
traces should be sent off. If an error occurs, a message will be displayed in
the console, and changes can be made as needed.

Profiling
~~~~~~~~~

Profiling can also be auto enabled with :ref:`ddtracerun` by providing the
``DD_PROFILING_ENABLED`` environment variable::

    DD_PROFILING_ENABLED=true ddtrace-run python app.py

If ``ddtrace-run`` isn't suitable for your application then
``ddtrace.profiling.auto`` can be used::

    import ddtrace.profiling.auto


OpenTracing
-----------

``ddtrace`` also provides an OpenTracing API to the Datadog tracer so
that you can use the Datadog tracer in your OpenTracing-compatible
applications.

Installation
~~~~~~~~~~~~

Include OpenTracing with ``ddtrace``::

  $ pip install ddtrace[opentracing]

To include the OpenTracing dependency in your project with ``ddtrace``, ensure
you have the following in ``setup.py``::

    install_requires=[
        "ddtrace[opentracing]",
    ],

Configuration
~~~~~~~~~~~~~

The OpenTracing convention for initializing a tracer is to define an
initialization method that will configure and instantiate a new tracer and
overwrite the global ``opentracing.tracer`` reference.

Typically this method looks something like::

    from ddtrace.opentracer import Tracer, set_global_tracer

    def init_tracer(service_name):
        """
        Initialize a new Datadog opentracer and set it as the
        global tracer.

        This overwrites the opentracing.tracer reference.
        """
        config = {
          'agent_hostname': 'localhost',
          'agent_port': 8126,
        }
        tracer = Tracer(service_name, config=config)
        set_global_tracer(tracer)
        return tracer

For more advanced usage of OpenTracing in ``ddtrace`` refer to the
documentation :ref:`here<adv_opentracing>`.
