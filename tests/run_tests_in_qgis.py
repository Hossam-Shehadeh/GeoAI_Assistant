"""
Run Tests in QGIS Python Console
This version works in QGIS where __file__ is not defined
"""

import unittest
import sys
import os

# Hardcoded path for QGIS Python Console
PLUGIN_DIR = '/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/GeoAI_Assistant_Pro'
sys.path.insert(0, PLUGIN_DIR)

def discover_and_run_tests():
    """Discover and run all tests"""
    # Discover tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    test_modules = [
        'tests.test_llm_handler',
        'tests.test_error_fixer',
        'tests.test_sql_queries',
        'tests.test_integration',
        'tests.test_edge_cases',
    ]
    
    for module_name in test_modules:
        try:
            tests = loader.loadTestsFromName(module_name)
            suite.addTests(tests)
            print(f"✅ Loaded tests from {module_name}")
        except Exception as e:
            print(f"⚠️  Could not load {module_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n" + "="*70)
        print("FAILURES:")
        print("="*70)
        for test, traceback in result.failures:
            print(f"\n{test}")
            print(traceback)
    
    if result.errors:
        print("\n" + "="*70)
        print("ERRORS:")
        print("="*70)
        for test, traceback in result.errors:
            print(f"\n{test}")
            print(traceback)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = discover_and_run_tests()
    sys.exit(0 if success else 1)

# For QGIS Python Console - just run directly
if __name__ != "__main__":
    discover_and_run_tests()


