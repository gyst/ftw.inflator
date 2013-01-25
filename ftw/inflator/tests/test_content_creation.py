from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from ftw.inflator.testing import INFLATOR_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from unittest2 import TestCase


class FooCreationLayer(PloneSandboxLayer):

    defaultBases = (INFLATOR_FIXTURE, )
    def setUpPloneSite(self, portal):
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['Folder'],
                                      'simple_publication_workflow')

        applyProfile(portal, 'ftw.inflator.tests:foo_creation')


FOO_FIXTURE = FooCreationLayer()
FOO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FOO_FIXTURE, ), name="ftw.inflator:FOO Integration")


class TestContentCreation(TestCase):

    layer = FOO_INTEGRATION_TESTING

    def setUp(self):
        super(TestContentCreation, self).setUp()
        self.portal = self.layer['portal']

    def test_foo_folder_type(self):
        foo = self.portal.get('foo')
        self.assertNotEqual(foo, None, 'Folder /foo not created')

        self.assertEqual(
            foo.portal_type, 'Folder',
            '/foo has wrong type "%s" but should be "Folder"' % (
                foo.portal_type))

    def test_foo_folder_title(self):
        foo = self.portal.get('foo')
        self.assertNotEqual(foo, None, 'Folder /foo not created')

        self.assertEqual(
            foo.Title(), 'Foo',
            '/foo has wrong Title "%s" but should be "Foo"' % foo.Title())

    def test_foo_folder_catalog(self):
        foo_path = '/'.join(self.portal.get('foo').getPhysicalPath())
        query = {'path': {'query': foo_path,
                          'depth': 0}}

        catalog = getToolByName(self.portal, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(query)
        self.assertEqual(len(brains), 1)

        foo_brain = brains[0]
        self.assertEqual(foo_brain.portal_type, 'Folder')
        self.assertEqual(foo_brain.Title, 'Foo')

    def test_foo_folder_workflow_state(self):
        foo = self.portal.get('foo')
        context_state = foo.unrestrictedTraverse('@@plone_context_state')
        review_state = context_state.workflow_state()
        self.assertEqual(review_state, 'published')

    def test_foo_folder_properties(self):
        foo = self.portal.get('foo')
        self.assertEqual(foo.getProperty('f\xc3\xbc\xc3\xbc'), 'b\xc3\xa4r')

    def test_foo_folder_constraintypes(self):
        foo = self.portal.get('foo')

        self.assertEqual(foo.getConstrainTypesMode(),
                         constraintypes.ENABLED,
                         'Constraint types are not enabled on folder foo')

        self.assertEqual(foo.getImmediatelyAddableTypes(),
                         ('Folder',),
                         'Immediately addable types are not configured well')

        self.assertEqual(foo.getLocallyAllowedTypes(),
                         ('Folder', 'Document'),
                         'Locally addable types are not configured well')
