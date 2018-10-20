#!/usr/bin/env python3
# coding:utf-8
import unittest
import time

from .. import Schedium


class SchediumBasicTestCase(unittest.TestCase):

    def test_urcase(self):
        sche = Schedium()

        _check_dict = {}

        def test_later(var, var1="test"):
            self.assertTrue(var1 == "test1", "indeed var1: {}".format(var1))
            _check_dict["basic_case_later"] = True

        print("test the execute_later")
        sche.execute_later(after=1, target=test_later, vargs=(1,), kwargs={"var1": "test1"})

        time.sleep(1.5)
        self.assertIn("basic_case_later", _check_dict)

        def test_now(var, var1="test"):
            self.assertTrue(var1 == "test2")
            _check_dict["now"] = True

        sche.execute_now(target=test_now, vargs=(1,), kwargs={"var1": "test2"})

        time.sleep(0.2)
        self.assertIn("now", _check_dict)

        print("start test interval")
        def test_interval(var, var1="test"):
            self.assertEqual(var1, "test3")

            if "interval" not in _check_dict:
                _check_dict["interval"] = 1
            else:
                _check_dict["interval"] += 1

        sche.execute_interval(interval=1, target=test_interval, vargs=(1,), kwargs={"var1": "test3"},
                              first=True, start=None, end=None, id="test")

        time.sleep(0.2)
        self.assertEqual(_check_dict["interval"], 1)
        time.sleep(1)
        self.assertEqual(_check_dict["interval"], 2)
        time.sleep(1)
        self.assertEqual(_check_dict["interval"], 3)

        sche.cancel("test")

        time.sleep(1)
        self.assertEqual(_check_dict["interval"], 3)


if __name__ == '__main__':
    unittest.main()
