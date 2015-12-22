from distutils.core import setup

setup(name='Qit',
      version='0.1',
      description='Prototyping environment for theoretical computer science',
      author='Qit Team',
      author_email='stanislav.bohm@vsb.cz',
      url='https://github.com/spirali/qit/',
      package_dir = { 'qit' : 'src/qit' },
      packages=['qit',
                'qit.base',
                'qit.domains',
                'qit.build',
                'qit.functions'],
     )
