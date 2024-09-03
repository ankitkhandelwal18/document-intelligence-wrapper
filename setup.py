# setup.py
from setuptools import setup, find_packages

setup(
    name='document_intelligence_wrapper',
    version='1.0.0b1',
    description='A wrapper around Azure Document Intelligence for processing PDFs and extracting text.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ankit Khandelwal',
    author_email='ankitkhandelwal18@icloud.com',
    url='https://github.com/ankitkhandelwal18/document-intelligence-wrapper',
    packages=find_packages(),
    install_requires=[
        'tabulate==0.9.0',
        'azure-ai-documentintelligence==1.0.0b3',
        'pandas==2.2.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)

