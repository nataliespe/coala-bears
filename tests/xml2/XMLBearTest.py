import os
import unittest

from queue import Queue
from bears.xml2.XMLBear import XMLBear
from coalib.testing.BearTestHelper import generate_skip_decorator
from coalib.testing.LocalBearTestHelper import verify_local_bear, execute_bear
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.settings.Section import Section
from coala_utils.ContextManagers import prepare_file


def load_testdata(filename):
    path = os.path.join(os.path.dirname(__file__),
                        'test_files',
                        filename)
    with open(path) as f:
        return f.read()


valid_xml_file = """<?xml version="1.0"?>
<a/>
"""

# The <?xml version="1.0"?> header is missing. This is no actual syntax error,
# but will be suggested from xmllint as a fix.
invalid_xml_file = """
<a>blah</a>
"""

invalid_xml_chars = """<?xml version="1.0"?>
<a>hey & hi</a>
"""

valid_xml_chars = """<?xml version="1.0"?>
<a>hey and hi</a>
"""

dtd_file = os.path.join(os.path.dirname(__file__),
                        'test_files',
                        'note.dtd')

schema_file = os.path.join(os.path.dirname(__file__),
                           'test_files',
                           'note.xsd')
relaxng_file = os.path.join(os.path.dirname(__file__),
                            'test_files',
                            'note.rng')

valid_xml_path = load_testdata('note.xml')
valid_xml_url = load_testdata('concept-valid.xml')
invalid_xml_schema = load_testdata('xsd-error.xml')
invalid_xml_dtd = load_testdata('dtd-error.xml')
invalid_xml_relaxng = load_testdata('rng-error.xml')
invalid_xml_url = load_testdata('concept-invalid.xml')

dtd_url = 'http://docs.oasis-open.org/dita/v1.0.1/dtd/concept.dtd'

XMLBearCorrectedTest = verify_local_bear(
    XMLBear,
    valid_files=(valid_xml_file, valid_xml_chars),
    invalid_files=(invalid_xml_file, invalid_xml_chars),
    tempfile_kwargs={'suffix': '.xml'})

XMLBearSchemaTest = verify_local_bear(
    XMLBear,
    valid_files=(valid_xml_path,),
    invalid_files=(invalid_xml_schema,),
    settings={'xml_schema': schema_file},
    tempfile_kwargs={'suffix': '.xml'})

XMLBearDTDPathTest = verify_local_bear(
    XMLBear,
    valid_files=(valid_xml_path,),
    invalid_files=(invalid_xml_dtd,),
    settings={'xml_dtd': dtd_file},
    tempfile_kwargs={'suffix': '.xml'})

XMLBearDTDUrlTest = verify_local_bear(
    XMLBear,
    valid_files=(valid_xml_url,),
    invalid_files=(invalid_xml_url,),
    settings={'xml_dtd': dtd_url},
    tempfile_kwargs={'suffix': '.xml'})

XMLBearRelaxNGTest = verify_local_bear(
    XMLBear,
    valid_files=(valid_xml_path,),
    invalid_files=(invalid_xml_relaxng,),
    settings={'xml_relaxng': relaxng_file},
    tempfile_kwargs={'suffix': '.xml'})


@generate_skip_decorator(XMLBear)
class XMLBearSeverityTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.uut = XMLBear(self.section, Queue())

    def test_info(self):
        content = invalid_xml_file.splitlines()
        with prepare_file(content, None) as (file, fname):
            with execute_bear(self.uut, fname, file) as results:
                self.assertEqual(results[0].severity, RESULT_SEVERITY.INFO)

    def test_errors(self):
        content = invalid_xml_chars.splitlines()
        with prepare_file(content, None) as (file, fname):
            with execute_bear(self.uut, fname, file) as results:
                self.assertEqual(results[0].severity, RESULT_SEVERITY.MAJOR)
