# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test

# Extnsion for writing UI tests (simulate UI interaction)
import omni.kit.ui_test as ui_test

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
import omni.FreeD.LiveLink


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class Test(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_freed_public_function(self):
        result = omni.FreeD.LiveLink.some_public_function(4)
        self.assertEqual(result, 256)


    async def test_window_button(self):

        # Find a label in our window
        label = ui_test.find("FreeD Live Link//Frame/**/Label[*]")

        # Find buttons in our window
        test_button = ui_test.find("FreeD Live Link//Frame/**/Button[*].text=='Start'")

        await test_button.click()
        #self.assertEqual(label.widget.text, "count: 1")

        await test_button.click()
        #self.assertEqual(label.widget.text, "count: 2")
