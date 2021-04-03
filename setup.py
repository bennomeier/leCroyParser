from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='lecroyparser',
      version='1.4.2',
      description='Parse LeCroy Binary Files.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Physics'],
      keywords='LeCroy Binary Scope Parse',
      url='http://github.com/bennomeier/lecroyparser',
      author='Benno Meier',
      author_email='meier.benno@gmail.com',
      license='MIT',
      packages=['lecroyparser'],
      include_package_data=True,
            install_requires = [
          'numpy',
          ],
      zip_safe=False)

