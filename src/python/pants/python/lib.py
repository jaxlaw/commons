# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed to the Apache Software Foundation (ASF) under one or more contributor license
# agreements.  See the NOTICE file distributed with this work for additional information regarding
# copyright ownership.  The ASF licenses this file to you under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

__author__ = 'John Sirios'

from pants import (
  Builder,
  PythonTarget,
  PythonTests,
)

import os
import subprocess

class PythonBuilder(Builder):
  def __init__(self, ferror, root_dir):
    Builder.__init__(self, ferror, root_dir)

  def build(self, target, is_meta, args):
    assert isinstance(target, PythonTarget), \
      "PythonBuilder can only build PythonTargets, given %s" % str(target)

    if isinstance(target, PythonTests):
      return self._run_tests(target, args)

    raise Exception("PythonBuilder cannot handle target: %s" % str(target))

  def _run_tests(self, target, args):
    template_data = target._create_template_data()

    testargs = [ 'py.test' ]
    if args:
      testargs.extend(args)

    def add_tests(template_data):
      if template_data.sources:
        basedir = template_data.template_base
        testargs.extend(os.path.join(basedir, test) for test in template_data.sources)

      if template_data.dependencies:
        for dependency in template_data.dependencies:
          add_tests(dependency.resolve()._create_template_data())

    add_tests(template_data)

    print 'PythonBuilder executing (PYTHONPATH="%s") %s' % (
      os.environ['PYTHONPATH'],
      ' '.join(testargs)
    )

    return subprocess.call(testargs, cwd = self.root_dir)
